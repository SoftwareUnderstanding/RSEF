from RSEF.repofrompaper.utils.helpers import clean_final_sentence
from RSEF.extraction.pdf_extraction_tika import read_pdf_list
from typing import List, Dict, Tuple
import re


def extract_references(pdf_list: List[str]) -> Tuple[Dict[str, str], List[str]]:
    '''
    Extracts references from a list of paragraphs. 
    Returns a dictionary with the references and a list of non-references.
    '''
    references, not_references = {}, []
    skip_until = None
    pattern = r'^\[\d{1,2}\]\s'

    for id, paragraph in enumerate(pdf_list):
        if len(paragraph.replace(" ", '').replace('\n', '')) < 10:
            continue

        if skip_until is not None and id < skip_until:
            # This paragraph is part of a previous reference
            continue
        else:
            skip_until = None

        # Check if the paragraph begins with number in a bracket
        if re.match(pattern, paragraph):
            next_paragraph_id = None
            # Search at most 10 next paragraphs until the next paragraph that begins with brackets
            for i in range(1, 10):
                if id+i < len(pdf_list) and pdf_list[id+i][0] == '[':
                    next_paragraph_id = id+i
                    break

            next_paragraph_id = next_paragraph_id if next_paragraph_id is not None else id + \
                3  # Most likely the last reference

            # Concatenate the paragraphs until the next paragraph that begins with brackets
            paragraph = ' '.join(pdf_list[id:next_paragraph_id])

            # Remove newline characters
            paragraph = paragraph.replace('\n', ' ')

            # Use regular expression to replace multiple spaces with a single space
            paragraph = re.sub(r'\s+', ' ', paragraph)

            # Remove leading and trailing spaces
            paragraph = paragraph.strip()

            # Skip the next paragraphs
            skip_until = next_paragraph_id

            paragraph = clean_final_sentence(paragraph)

            # The paragraph is a reference in the format of [number] Author, Title, Journal, Year
            # Use the [number] as key and the rest as value for the references dictionary
            references[f"[{paragraph.split(']')[0][1:]}]"] = paragraph.replace(
                f"[{paragraph.split(']')[0][1:]}] ", '').strip()
        else:
            not_references.append(paragraph)

    return references, not_references


def extract_full_sentences(pdf_list: List[str]) -> Tuple[List[str], List[str]]:
    '''
    Extracts full sentences from a list of paragraphs. 
    Returns a list of full sentences and a list of non-full sentences.
    A full sentence is a sentence that begins with a capital letter and ends with a period.
    '''
    full_sentences, not_final_sentences = [], []
    for paragraph in pdf_list:
        if len(paragraph.replace(" ", '').replace('\n', '')) < 10:
            continue

        # Split sentences with period and capital letter
        paragraph = re.sub(r'(\.\s)([A-Z])', r'\1\n \2', paragraph)

        if '\n' in paragraph:
            paragraph = clean_final_sentence(paragraph)

            new_paragraph = []
            for sentence in paragraph.replace('.', '..').split('. '):
                if not sentence and len(sentence) < 1:
                    continue

                # Last item may have two periods
                sentence = sentence.replace('..', '.')

                # If sentence begins with a capital letter and ends with a period, add to new_paragraph
                try:
                    if sentence[0].isupper() and sentence[-1] == '.' and len(sentence) > 20:
                        full_sentences.append(sentence)
                    else:
                        new_paragraph.append(sentence)
                except Exception as e:
                    pass

            if new_paragraph:
                not_final_sentences.extend(new_paragraph)
        elif paragraph[0].isupper() and paragraph[-1] == '.' and len(paragraph) > 20:
            full_sentences.append(paragraph)
            paragraph = ''
        elif re.match(r'^\[\d{1,2}\]\s', paragraph) and paragraph[-1] == '.' and len(paragraph) > 20:
            full_sentences.append(paragraph)
            paragraph = ''
        else:
            not_final_sentences.append(paragraph)

    return full_sentences, not_final_sentences


def combine_split_sentences(sentences: List[str]) -> Tuple[List[str], List[str]]:
    '''
    Combines split sentences and returns a list of combined sentences and a list of non-combined sentences.
    A sentence is combined if it begins with a capital letter and does not end with a period, 
    and the next sentence begins with a lowercase letter and ends with a period.
    '''
    final_sentences, uncombined_sentences = [], []
    skip_next = False
    for id, paragraph in enumerate(list(sentences)):
        if skip_next:
            # Skip the next paragraph because it was combined with the previous one
            skip_next = False
            continue

        # Check if first letter is capital, and first letter of next paragraph is lowercase and last is period
        if paragraph[-1] not in ['.', ':'] and paragraph[0].isupper():
            if id < len(sentences) - 1 and sentences[id+1][-1] == '.':
                sentence = paragraph + ' ' + sentences[id+1]

                # Use regular expression to replace multiple spaces with a single space
                sentence = re.sub(r'\s+', ' ', sentence)

                # Remove word break hyphen if its not a link, else just replace the space
                sentence = sentence.replace('- ', '')

                # Clean the sentence
                sentence = clean_final_sentence(sentence)

                final_sentences.append(sentence)
                skip_next = True
            else:
                uncombined_sentences.append(paragraph)
        else:
            uncombined_sentences.append(paragraph)

    # Replaces word breaks in the sentences
    combined_not_final_sentences = '#JOIN#'.join(
        uncombined_sentences).replace('-#JOIN# ', '').split('#JOIN#')
    combined_not_final_sentences = ' '.join(
        combined_not_final_sentences).replace('. ', '.. ').split('. ')
    combined_not_final_sentences = [clean_final_sentence(
        s) for s in combined_not_final_sentences if len(s) > 20]

    return final_sentences, combined_not_final_sentences


def extract_footnotes(pdf_list: List[str]) -> dict:
    '''
    Extracts footnotes by looking for numbers in the text followed by a link. 
    Returns a dictionary with the number as key and the link as value.
    '''
    LINK_REGEX = r'\b(\d+)\s*(https?://(?:www\.)?(?:github\.com|gitlab\.com)/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)\b'

    matches_dict = {}
    for sentence in pdf_list:
        matches = re.findall(LINK_REGEX, sentence)
        sentence_matches = {number: link for number, link in matches}
        matches_dict.update(sentence_matches)

    return matches_dict


def get_sentences(pdf_path: str) -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
    '''Extracts references, footnotes and sentences from a pdf file.'''
    # Read the pdf file with Tika
    pdf_list = read_pdf_list(pdf_path, splitter='\n\n')

    # Extract reference sentences and non-reference sentences
    references, not_final_sentences = extract_references(pdf_list)

    # Extract full sentences which begin with a capital letter and end with a period
    final_sentences, not_final_sentences = extract_full_sentences(
        not_final_sentences)

    combined_final, not_final_sentences = combine_split_sentences(
        not_final_sentences)

    final_sentences.extend(combined_final)

    footnotes = extract_footnotes(
        final_sentences + not_final_sentences + list(references.values()))

    return references, footnotes, final_sentences + not_final_sentences
