import logging

import requests
import json
from fuzzywuzzy import fuzz
from urllib.parse import quote
from ...utils.regex import str_to_doiID, str_to_arxivID

BASE_URL = 'https://api.openalex.org/works'

log = logging.getLogger(__name__)

def create_arxiv_doi(arxiv):
    # Every arxiv after 2022 has an automatically generated doi like the one below
    base_doi = "https://doi.org/10.48550/arXiv."
    if arxiv_id := str_to_doiID(arxiv):
        return base_doi + arxiv_id
    return None

def query_openalex_api(doi):
    """
    @Param String doi: DOI Identifier\
    -----
    returns JSON of Open Alex response
    """
    doi_url = convert_to_doi_url(doi)
    if doi_url is None:
        return None
    url = BASE_URL + "/" + doi_url
    try:
        response = requests.get(url)
        if response.status_code != 200:
            log.debug("HTTP request failed with status code: %s", response.status_code)
            return None
        data = response.json()
        return data
    except json.JSONDecodeError as e:
        log.error("Error decoding JSON response: %s", str(e))
    except Exception as e:
        log.error("Other Error has been produced %s", str(e))
    return None


def convert_to_doi_url(input_string):
    """
    @Param input_string: possible DOI to be converted to DOI URL
    :returns String: DOI URL or None
    """
    doi = str_to_doiID(input_string)
    if doi is not None:
        doi_url = 'https://doi.org/' + doi.strip()
        return doi_url
    return None


#TODO change the pdf naming system and this function
# def pdf_name_to_meta(pdf_folder,path_out):
#
#     list_datas = []
#     for file in os.listdir(pdf_folder):
#         if file.endswith(".pdf"):
#             doi = file.replace("_","/").replace(".pdf",'')
#             data = query_openalex_api(doi)
#             list_datas.append(data)
#     with open(path_out, 'w') as json_file:
#         json.dump(list_datas, json_file, indent=4)

#TODO need to create a way to double check the pdf title vs the one extracted
#TODO ensure that the first option in the returned list is the one I want

def _verify_title(response_json, og_title):
    """
    Give the correct result by comparing titles based on a fuzzy matching ratio.

    :param response_json: JSON response from the search.
    :param original_title: PDF title to match against.
    :return: Metadata of result if the titles match.
    """
    fuzzy_threshold = 85
    try:
        results = response_json["results"]
    except KeyError:
        return None
    for result in results:
        try:
            title = result['title']
        except:
            continue
        if (fuzz.partial_ratio(og_title.lower(), title.lower())) > fuzzy_threshold:
            return result
    print("Work not found within OpenAlex")
    return None

def pdf_title_to_meta(title):
    """

    """
    if title == None or title == "":
        return None
    title_url = quote(title)
    url = BASE_URL + "?filter=title.search:" + title_url
    try:
        response = requests.get(url)
        print("This is the open alex response " + str(response.status_code))
        if response.status_code == 200:

            return _verify_title(response_json=response.json(), og_title=title)
        else:
            raise requests.RequestException(f"Error: {response.status_code}")
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {str(e)}")


#input = '../../corpus_papers_w_code/papers_with_code'
#pdf_name_to_meta(input,'./penis.json')

#txt_to_meta('./dois.txt','./pls.json')