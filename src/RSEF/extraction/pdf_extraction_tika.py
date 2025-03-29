import collections
import logging
import os
import re
from tika import parser
# Import REGEXes
from ..utils.regex import ZENODO_DOI_REGEX, ZENODO_RECORD_REGEX, GITHUB_REGEX, GITLAB_REGEX

log = logging.getLogger(__name__)


# ======================================================================================================================
# READ THE PDF
# ======================================================================================================================


def raw_read_pdf(pdf_path) -> str:
    if not pdf_path:
        return ""
    try:
        path = os.path.expandvars(pdf_path)
        parsed = parser.from_file(path)
        content = parsed.get('content', None)
        if not content:
            log.debug("Issue when retrieving pdf content TIKA")
        return content
    except FileNotFoundError:
        log.error(f"PDF file not found at path: {pdf_path}")
        return ""
    except Exception as e:
        log.error(f"An error occurred while reading the PDF: {str(e)}")
        return ""


def raw_to_list(raw_pdf_data: str) -> list:

    if not raw_pdf_data:
        log.debug(f"converting from raw pdf to list pdf, {raw_pdf_data}")
        return []

    list_pdf_data = raw_pdf_data.split('\n')
    return [x for x in list_pdf_data if x != '']


def read_pdf_list(pdf_path, splitter='\n') -> list:
    try:
        raw = parser.from_file(pdf_path)
        list_pdf_data = raw['content'].split(splitter)
        # delete empty lines
        list_pdf_data = [x for x in list_pdf_data if x != '']

        return list_pdf_data

    except FileNotFoundError:
        log.error(f"PDF file not found at path: {pdf_path}")
        return []
    except Exception as e:
        log.error(f"An error occurred while reading the PDF: {str(e)}")
        return []
# ======================================================================================================================
# TITLE EXTRACTION
# ======================================================================================================================


def get_possible_title(pdf_path):
    pdf_raw = raw_read_pdf(pdf_path)
    if not pdf_raw:
        return None
    return extract_possible_title(pdf_raw)


def extract_possible_title(pdf_raw_data: str):
    """
    Given raw data, this function attempts to extract a possible title.
    ASSUMPTION: The title is assumed to be the first non-line break character and ends with two line breaks \n\n
    :param pdf_raw_data: String of raw PDF data
    --
    :return: Possible title (String), or None if not found
    """
    poss_title = ""
    found_first_char = False
    previous_was_newline = False
    for i in pdf_raw_data:
        if not found_first_char:
            if i != '\n':
                found_first_char = True
                poss_title = poss_title + i
            else:
                continue
        else:
            if i == '\n' and previous_was_newline:
                return poss_title[:-1]
            elif i == '\n':
                previous_was_newline = True
                poss_title = poss_title + " "
            else:
                previous_was_newline = False
                poss_title = poss_title + i
    return None

# ======================================================================================================================
# ABSTRACT EXTRACTION
# ======================================================================================================================


def find_abstract_index(pdf_data: list) -> int:
    index = 0
    try:
        for line in pdf_data:
            if "abstract" in line.lower():
                if index < len(pdf_data):
                    return index
            index += 1
    except Exception as e:
        log.warning(f"Failed to Extract the abstract {str(e)}")
        return -1
    return index


def get_possible_abstract(pdf_data: list) -> str:
    try:
        index = find_abstract_index(pdf_data)
        if index > 0:
            return ''.join(pdf_data[index:index+50])
    except Exception as e:
        log.error(f"get_possible_abstract: Issue while trying to extract the abstract: {e}")


def find_github_in_abstract(pdf_data: list) -> list:
    abstract_index = find_abstract_index(pdf_data)
    if abstract_index > 0:
        return look_for_github_urls(pdf_data[abstract_index:abstract_index:50])


# ======================================================================================================================
# EXTRACT GIT
# ======================================================================================================================

# regular expression to get all the urls, returned as a list
def get_git_urls(text: str) -> list:
    """
    Returns
    -------
    List Strings (urls)

    """
    urls_github = re.findall(GITHUB_REGEX, text)
    urls_gitlab = re.findall(GITLAB_REGEX, text)
    urls = urls_github + urls_gitlab
    return urls


def clean_up_git_url(git_url_list: list) -> list:
    clean_urls = []
    for url in git_url_list:
        # Remove 'www.' if it exists
        url = url.replace("www.", "")
        # Strip the trailing period if it exists
        if url.endswith('.'):
            url = url[:-1]
        # Strip '.git' if it exists
        if url.endswith('.git'):
            url = url[:-4]
        # Prepend 'https://' if the URL starts with 'github.com'
        if url.startswith('github.com'):
            url = 'https://' + url
        clean_urls.append(url)
    return clean_urls



def look_for_github_urls(list_pdf_data: list) -> list:
    git_urls = []
    for value in list_pdf_data:
        results = get_git_urls(value)
        if results:
            git_urls.extend(results)
    git_urls = clean_up_git_url(git_urls)
    return git_urls


def ranked_git_url(pdf_data: list):
    """
    Creates  ranked list of GitHub urls and count pairs or false if none are available
    Returns
    -------
    List Strings (urls)
    --
    Else (none are found)
        False
    """
    try:
        github_urls = look_for_github_urls(pdf_data)
        if github_urls:
            return rank_elements(github_urls)
        else:
            return None
    except Exception as e:
        print(str(e))

# ======================================================================================================================
# EXTRACT ZENODO
# ======================================================================================================================


def get_zenodo_urls(text: str) -> list:
    """
    Returns
    -------
    List Strings (urls)

    """
    urls_doi = re.findall(ZENODO_DOI_REGEX, text)
    urls_records = re.findall(ZENODO_RECORD_REGEX, text)
    zenodo_urls = urls_doi + urls_records

    return zenodo_urls


def ranked_zenodo_url(raw_pdf_data: str):
    """
    Creates  ranked list of GitHub urls and count pairs or false if none are available
    Returns
    -------
    List Strings (urls)
    --
    Else (none are found)
        False
    """
    try:
        zenodo_urls = get_zenodo_urls(raw_pdf_data)
        if zenodo_urls:
            return rank_elements(zenodo_urls)
        else:
            return None
    except Exception as e:
        print(str(e))

# ======================================================================================================================
# EXTRACT URLs
# ======================================================================================================================


def extract_urls(raw_pdf_data: str, list_pdf_data: list) -> dict:
    # TODO optimise
    #list_pdf_data = raw_to_list(raw_pdf_data)
    urls = {}
    if not raw_pdf_data:
        log.debug("Extract Urls: raw_pdf_data is None or Empty")
        return urls
    if not list_pdf_data:
        log.debug("Extract Urls: list_pdf_data is None or Empty")
        return urls

    list_git_urls = ranked_git_url(list_pdf_data)
    list_zenodo_urls = ranked_zenodo_url(raw_pdf_data)

    if list_git_urls:
        urls['git'] = list_git_urls
    if list_zenodo_urls:
        urls['zenodo'] = list_zenodo_urls

    return urls


def rank_elements(url_list: list) -> list:
    """
    Takes a list of strings (URLs)

    Returns
    --------
    List of dictionaries. Each dictionary contains 'url' (String) as key and the number of appearances as value.
    Ordered, High to Low, based on the number of appearances.
    """
    counts = collections.defaultdict(int)
    for url in url_list:
        counts[url] += 1

    ranked_list = [{'url': url, '#_appearances': count} for url, count in counts.items()]
    ranked_list.sort(key=lambda x: (x['#_appearances'], x['url']), reverse=True)

    return ranked_list



