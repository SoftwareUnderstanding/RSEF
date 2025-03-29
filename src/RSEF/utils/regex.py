import re

DOI_REGEX = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>,])\S)+)\b'
ARXIV_REGEX = r'.*(\d{4}\.\d{4,5}).*'
# ZENODO
ZENODO_DOI_REGEX = r'https?:\/\/doi\.org\/10.5281/zenodo.[0-9]+'
ZENODO_RECORD_REGEX = r'https?://zenodo.org/records/[0-9]+'
ZENODO_SINGLE_RECORD_REGEX = r'https?://zenodo.org/record/[0-9]+'
# GIT
# GITHUB_REGEX = r'(https?://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)'
# GITLAB_REGEX = r'(https?://gitlab.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)'
GITHUB_REGEX = r'(?:https?://(?:www\.)?)?github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+'
GITLAB_REGEX = r'(?:https?://(?:www\.)?)?gitlab\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+'


def str_to_doiID(string):
    try:
        match = re.search(DOI_REGEX, string)
        if match:
            doi = match.group(1).replace('.pdf', '')
            return doi
        return None
    except:
        return None


def str_to_doi_list(string):
    if not string:
        return None
    pattern = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'
    matches = re.findall(pattern, string)
    return matches if len(matches) > 0 else None


def str_to_arxivID(string):
    try:
        match = re.search(ARXIV_REGEX, string)
        if match:
            arxiv = match.group(1)
            return arxiv
        return None
    except:
        return None


def str_to_arxiv_list(string):
    if not string:
        return None
    pattern = r'.*(\d{4}\.\d{4,5}).*'
    matches = re.findall(pattern, string)
    return matches if len(matches) > 0 else None


# TODO change the _ for ! in the filename doi. Alsolook at unpaywall_pdf_downloader
def adrian_is_filename_doi(file_name):
    """
    Regex on the file name and return it if it is of DOI ID format.
    Returns
    -------
    List Strings (doi's)
    """

    file_name = file_name.replace('_', '/').replace('.pdf', '').replace('-DOT-', '.')
    match = re.search(DOI_REGEX, file_name)
    if match:
        return file_name
    else:
        return False


def adrian_filename_to_doi_convert(file_name):
    poss_doi = file_name.replace('_', '/').replace('.pdf', '').replace('-DOT-', '.')
    match = re.search(DOI_REGEX, poss_doi)
    if match:
        return match.group(1)
    return None