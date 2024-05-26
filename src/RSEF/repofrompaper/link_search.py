
from typing import List, Dict, Tuple, Optional
from .utils.constants import REPO_REGEXES
import re


def find_repo_links(text: str) -> List[str]:
    """Extracts repository links from a given text using regex."""
    found_links = []
    for regex in REPO_REGEXES:
        found_links += re.findall(regex, text)
    return found_links


# Search for the link in the references, footnotes and sentences
def find_link_in_references(reference_numbers: List[str], references: Dict[str, str]) -> Optional[str]:
    """Find the link in the references dictionary for the given reference numbers"""
    for ref in reference_numbers:
        if ref in references:
            repo_links = find_repo_links(references[ref])
            if repo_links:
                link = repo_links[0]
                print(f'Found {link} in references dictionary using {ref} reference number')
                return link, ref
    return None, None


def find_link_in_footnotes(all_footnotes: List[str], footnotes: Dict[str, str]) -> Optional[str]:
    """Find the link in the footnotes dictionary for the given footnotes"""
    # Look for footnotes in the footnotes dictionary
    for f in all_footnotes:
        if f in footnotes:
            link = footnotes[f]
            print(f'Found {link} in footnotes dictionary using footnote {f}')
            return link, f
    return None, None


def find_link_in_sentences(sentences_with_footnote: List[Tuple[str, str]]) -> Optional[str]:
    """Find the link in the sentences with footnote for the given footnotes"""
    # Look for link attached to the footnote in sentence
    for sentence_with_number, footnote_link, footnote in sentences_with_footnote:
        if footnote_link:
            link = footnote_link
            return link, footnote

    # Look for sentence that contains the footnote
    for sentence_with_number, footnote_link, footnote in sentences_with_footnote:
        repo_links = find_repo_links(sentence_with_number)
        if repo_links:
            link = repo_links[0]
            return link, footnote
    return None, None


def extract_link_by_number(sentence: str, target_number: str) -> str:
    """
    Extracts a link from a sentence that follows a given number. 
    Returns None if no link is found.
    """
    # This situations should be caught by the footnotes extraction, but just in case
    LINK_REGEX = re.escape(
        target_number) + r'\s*(https?://(?:www\.)?(?:github\.com|gitlab\.com)/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+))'
    match = re.search(LINK_REGEX, sentence)
    return match.group(1) if match else None


def get_sentences_with_footnote(footnotes: List[str], sentences: List[str], best_sentences: List[str]) -> List[Tuple[str, str]]:
    """Returns a list of sentences that contain a footnote and a link to a repository."""
    sentences_with_footnote = []
    for footnote in footnotes:
        for sentence in sentences:
            if str(footnote) in sentence \
                    and '.com' in sentence \
                    and ('github' in sentence or 'gitlab' in sentence) \
                    and sentence not in best_sentences:
                link = extract_link_by_number(sentence, str(footnote))
                sentences_with_footnote.append((sentence, link, str(footnote)))

    return sentences_with_footnote
