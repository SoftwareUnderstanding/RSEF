from .link_search import get_sentences_with_footnote, find_link_in_footnotes, find_link_in_references, find_link_in_sentences, find_repo_links
from ..extraction.pdf_extraction_tika import read_pdf_list
from .utils.constants import FOOTNOTE_NUM_LIMIT
from .sentence_extraction import get_sentences
from .model_inference import get_top_sentences
from .utils.helpers import clean_final_link
from typing import List, Tuple
import re

def extract_repo_links_from_pdf(pdf_path: str) -> Tuple[List[str], str]:
    """Extract the top sentences from the pdf and find the link"""
    # Get all sentences, footnotes and references from the pdf-to-text
    pdf_list = read_pdf_list(pdf_path, splitter='\n\n\n')
    references, footnotes, sentences = get_sentences(pdf_list)

    # Get the top sentences from the pdf with the model
    best_sentences = get_top_sentences(sentences)

    link, all_footnotes, reference_numbers = '', [], []
    source_para, number_sources = '', {}

    for sentence in best_sentences:
        # Look for github links
        repo_links = find_repo_links(sentence)

        if repo_links:
            link = repo_links[0]
            source_para = sentence
            break
        else:
            # Use regular expression to find numbers attached to words
            # Ensure non-duplication
            square_brackets = re.findall(r'\[\d+\]', sentence)
            if square_brackets:
                reference_numbers.extend(square_brackets)

            numbers = list(set(re.findall(r'(\[\d+\]|\d+)\S*\b', sentence)))

            # Remove numbers greater than 30
            numbers = [num for num in numbers if '[' not in num and 0 < int(
                num) <= FOOTNOTE_NUM_LIMIT]

            # If more than 5 numbers, unlikely to be footnotes
            numbers = numbers if len(numbers) <= 5 else []

            # Use regular expression to find special characters used as footnotes
            extra_chars = list(set(re.findall(r'[†‡*]', sentence)))
            all_footnotes.extend(numbers+extra_chars)
            
            # Store the sentence and its footnotes and references
            number_sources[sentence] = {'footnotes': numbers+extra_chars, 'references': square_brackets}

    if not link and reference_numbers:  # No link found in best matches, look for references or footnotes
        link, reference = find_link_in_references(reference_numbers, references)
        
        # If the link is found, store the source paragraph by looking for the reference number
        if link and reference:
            source_para = reference

    if not link and all_footnotes:
        # Remove duplicates in all_footnotes while keeping order
        all_footnotes = list(dict.fromkeys(all_footnotes))
        link, footnote = find_link_in_footnotes(all_footnotes, footnotes)

        if not link:
            sentences_with_footnote = get_sentences_with_footnote(
                all_footnotes, sentences, best_sentences)
            link, footnote = find_link_in_sentences(sentences_with_footnote)
            
        # If the link is found, store the source paragraph by looking for the footnote number
        if link and footnote:
            for key, value in number_sources.items():
                if footnote in value['footnotes']:
                    source_para = key
                    break
                
    return clean_final_link(link), source_para
