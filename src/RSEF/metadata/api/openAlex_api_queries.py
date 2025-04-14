import logging
import re
import requests
import json
from fuzzywuzzy import fuzz
from urllib.parse import quote
import unicodedata
from ...utils.regex import str_to_doiID

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
            log.debug("HTTP request failed with status code: %s",
                      response.status_code)
            return None
        data = response.json()
        return data
    except json.JSONDecodeError as e:
        log.error("Error decoding JSON response: %s", str(e))
    except Exception as e:
        log.error("Other Error has been produced %s", str(e))
    return None


def query_openalex_by_title(title):
    """
    Queries the OpenAlex API with a given title and returns the best-matched metadata using fuzzy matching.

    @param title: The (possibly noisy) title of the paper.
    @return: Best-matching metadata dict or None.
    """
    if not title:
        return None

    # Clean the title before search
    normalized_title = unicodedata.normalize("NFKD", title)
    cleaned_title = re.sub(r"[^a-zA-Z0-9 _-]+", '', normalized_title)
    title_url = quote(cleaned_title)
    url = f"{BASE_URL}?filter=title.search:{title_url}"
    log.debug("Querying OpenAlex API with URL: %s", url)

    try:
        response = requests.get(url)
        if response.status_code != 200:
            log.debug("HTTP request failed with status code: %s",
                      response.status_code)
            return None

        data = response.json()
        results = data.get("results", [])
        if not results:
            return None

        # Apply fuzzy matching to find the best match
        fuzzy_threshold = 85
        for result in results:
            candidate_title = result.get("title", "")
            if fuzz.partial_ratio(title.lower(), candidate_title.lower()) >= fuzzy_threshold:
                return result

        log.debug("No sufficiently close match found in OpenAlex")
        return None

    except json.JSONDecodeError as e:
        log.error("Error decoding JSON response: %s", str(e))
    except Exception as e:
        log.error("Other Error has been produced: %s", str(e))

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


# TODO change the pdf naming system and this function
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


# input = '../../corpus_papers_w_code/papers_with_code'
# pdf_name_to_meta(input,'./penis.json')

# txt_to_meta('./dois.txt','./pls.json')
