import json
import logging
from ..extraction.somef_extraction.somef_extractor import (
    find_doi_citation,
    description_finder,
    find_arxiv_citation,
    get_related_paper
)


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        logging.error("Error while trying to open the repository JSON")
        return None


def is_it_bidir(paper_obj, repo_json):
    """
    Checks if the paper relationship with the repository is bidirectional.

    :param paper_obj: An instance of the Paper class representing the paper.
    :param repo_json: A string representing the path to the JSON file of the repository.

    :returns:

    """
    if not (repo_data := load_json(repo_json)):
        logging.error("is_it_bidir: Error while trying to open repository JSON")
        return None
    bidir_locations = []
    if doi := paper_obj.doi:
        found_bidir = is_doi_bidir(doi, repo_data)
        if found_bidir:
            bidir_locations.extend(found_bidir)
    if arxiv := paper_obj.arxiv:
        found_bidir = is_arxiv_bidir(arxiv, repo_data)
        if found_bidir:
            bidir_locations.extend(found_bidir)
    if title := paper_obj.title:
        found_bidir = is_title_bidir(title, repo_data)
        if found_bidir:
            bidir_locations.extend(found_bidir)
    return bidir_locations

# ======================================================================================================================
# DOI BIDIR
# ======================================================================================================================


def is_doi_bidir(doi: str, repo_data: dict):

    bidir_citation = _doi_is_citation_bidir(doi, repo_data) or []
    bidir_description = _doi_is_description_bidir(doi, repo_data) or []

    return bidir_citation + bidir_description if bidir_citation or bidir_description else None


def _doi_is_citation_bidir(pp_doi: str, repo_data: dict):
    doi_cite = find_doi_citation(repo_data)
    if not doi_cite:
        return None

    entries = _citation_bidir(pp_doi, doi_cite, "DOI")

    return entries if entries else None


def _doi_is_description_bidir(pp_doi: str, repo_data: dict):
    """
    :param pp_doi: Paper's doi
    :param repo_data: dictionary from SOMEF repo json
    :returns:
    list of dictionaries
    """
    # run through description, if doi is found, will be within dictionary of lists
    doi_set = safe_dic(description_finder(repo_data), 'doi')
    result = []
    if doi_set:
        pp_doi = pp_doi.lower()
        for doi in doi_set:
            if not doi:
                continue
            if doi.lower() == pp_doi:
                result.append({
                    "location": "DESCRIPTION",
                    "id_type": "DOI",
                    "identifier": doi,
                    "source": "SOMEF"
                })
    return result


def _iterate_citations(citation_data: list, id_2_find: str) -> set:
    """
    :param citation_data:  List[(list[ID's], source_url string)]
    :returns:
    set of tuples
    tuple = (identifier: String , place: String)
    """
    id_2_find = id_2_find.lower()
    directional_citations = set()
    for ids, location in citation_data:
        if id_2_find in map(str.lower, ids):
            location_key = "README" if location and "readme" in location.lower() else "FILE"
            directional_citations.add((id_2_find, location_key if location else "SOMEF_ERROR"))
    return directional_citations


def _generate_citation_entries(bidir_tuples: set, format: str, id_type: str) -> list:
    """
    :param bidir_tuples: set (identifier: String , place: String)
    :param format: What citation format was used

    :returns: List of processed citation entries or None.
    """
    result = []
    for tup in bidir_tuples:
        entry = {
            "location": str(tup[1]) + "_" + str(format),
            "id_type": id_type,
            "identifier": tup[0],
            "source": "SOMEF"
        }
        result.append(entry)
    return result


def _citation_bidir(id_2_find: str, analysed_citation: dict, id_type: str) -> list:
    """
    :param id_2_find: String identifier to be found within the different citation formats available
    :param analysed_citation: {'CFF': [], 'BIBTEX': [], "TEXT": []} \
                               Each list containing tuples = (id, source_url) (str,str)
    :returns:
    list of dictionaries where the id has been found to be bidirectional
    """
    result = []
    for format_key in ["CFF", "BIBTEX", "TEXT"]:
        if format_data := analysed_citation.get(format_key):
            bidir = _iterate_citations(citation_data=format_data, id_2_find=id_2_find)
            result.extend(_generate_citation_entries(bidir, format_key, id_type))
    return result if len(result) > 0 else None


# ======================================================================================================================
# ARXIV BIDIR
# ======================================================================================================================

def is_arxiv_bidir(pp_arxiv, repo_data):
    """
       Returns:
        list: Combined results from description, citation, and related sections.
    """
    result = []

    desc = _arxiv_in_description(pp_arxiv, repo_data)
    citation = _arxiv_is_citation_bidir(pp_arxiv, repo_data)
    related = _arxiv_in_related(pp_arxiv, repo_data)

    if citation:
        result.extend(citation)
    if desc:
        result.append(desc)
    if related:
        result.append(related)

    return result


def _arxiv_in_description(pp_arxiv, repo_data):

    arxiv_set = safe_dic(description_finder(repo_data), 'arxiv')
    if arxiv_set is not None and pp_arxiv in arxiv_set:
        return {
            "location": "DESCRIPTION",
            "id_type": "ARXIV",
            "identifier": pp_arxiv,
            "source": "SOMEF"
        }
    else:
        return None


def _arxiv_in_related(pp_arxiv, repo_data):
    if arxivID_list := get_related_paper(repo_data):
        if arxivID_list is not None:
            if pp_arxiv in arxivID_list:
                return {
                    "location": "RELATED_PAPERS",
                    "id_type": "ARXIV",
                    "identifier": pp_arxiv,
                    "source": "SOMEF"
                }
    return None

def _arxiv_is_citation_bidir(pp_arxiv: str, repo_data: dict):
    arxiv_cite = find_arxiv_citation(repo_data)
    if not arxiv_cite:
        return None

    entries = _citation_bidir(pp_arxiv, arxiv_cite, "ARXIV")

    return entries if entries else None

# ======================================================================================================================
# TITLE BIDIR
# ======================================================================================================================


def is_title_bidir(pp_title: str, repo_data: dict):
    bidir = []
    # See if its within the citation
    results = safe_dic(repo_data, 'citation')
    citation_title = _citation_title(results, pp_title)
    if citation_title:
        bidir.append({
            "location": "CITATION" + "_" + citation_title,
            "id_type": "TITLE",
            "identifier": pp_title,
            "source": "SOMEF"
        })
    # See if its within the Description
    results = safe_dic(repo_data, 'description')
    title_found = _iterate_results(results, pp_title)
    if title_found:
        bidir.append({
            "location": "DESCRIPTION",
            "id_type": "TITLE",
            "identifier": pp_title,
            "source": "SOMEF"
        })

    poss_found = safe_dic(repo_data, 'full_title')
    if poss_found and type(poss_found) == str:
        title_found = poss_found.lower() == pp_title.lower
    if title_found:
        bidir.append({
            "location": "REPO_TITLE",
            "id_type": "TITLE",
            "identifier": pp_title,
            "source": "SOMEF"
        })

    return bidir

def _convert_source(source:str) -> str:

    return "README" if source and "readme" in source.lower() else "FILE"


def _citation_title(citation_results, title):
    if not citation_results:
        return None
    for citation in citation_results:
        result = safe_dic(citation, "result")
        value = safe_dic(result, 'value')
        if is_substring_found(title, value) or is_substring_found(value, title):
            source = safe_dic(citation, "source")
            return _convert_source(source) if source else "SOMEF ERROR"
    return None

def _iterate_results(results: dict, string_2_find: str) -> bool:
    if (not results) or (not string_2_find):
        return False
    for result in results:
        value = safe_dic(safe_dic(result, "result"), 'value')
        if value:
            return is_substring_found(string_2_find, value) or is_substring_found(value, string_2_find)
    return False


def is_substring_found(substring, larger_string) -> bool:
    """
    :param substring: The string you want to find
    :param larger_string: The string where you will look for the substring
    :returns:
    True: Found, False: Not found substr within string
    """
    if substring.lower() in larger_string.lower():
        return True
    else:
        return False

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None


def safe_list(list, i):
    try:
        return list[i]
    except:
        return None