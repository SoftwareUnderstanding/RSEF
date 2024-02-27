from RSEF.repofrompaper.utils.constants import CORPUS_PATH, FOOTNOTE_NUM_LIMIT
from RSEF.repofrompaper.utils.helpers import clean_final_link
import RSEF.repofrompaper.rfp.link_search as ls
from .sentence_extraction import get_sentences
from .model_inference import get_top_sentences
from typing import List, Tuple
import re

def extract_repo_links_from_pdf(pdf_path: str) -> Tuple[List[str], str]:
    '''Extract the top sentences from the pdf and find the link'''
    # Get all sentences, footnotes and references from the pdf-to-text
    references, footnotes, sentences = get_sentences(CORPUS_PATH + pdf_path)

    # Get the top sentences from the pdf with the model
    best_sentences = get_top_sentences(sentences)

    link, all_footnotes, reference_numbers = '', [], []

    for sentence in best_sentences:
        # Look for github links
        repo_links = ls.find_repo_links(sentence)

        if repo_links:
            link = repo_links[0]
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

    if not link and reference_numbers:  # No link found in best matches, look for references or footnotes
        link = ls.find_link_in_references(reference_numbers, references)

    if not link and all_footnotes:
        # Remove duplicates in all_footnotes while keeping order
        all_footnotes = list(dict.fromkeys(all_footnotes))
        link = ls.find_link_in_footnotes(all_footnotes, footnotes)

        if not link:
            sentences_with_footnote = ls.get_sentences_with_footnote(
                all_footnotes, sentences, best_sentences)
            link = ls.find_link_in_sentences(sentences_with_footnote)

    return best_sentences, clean_final_link(link)