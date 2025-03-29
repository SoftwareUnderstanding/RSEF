import json
from ..metadata.api.openAlex_api_queries import query_openalex_api
from ..metadata.metadata_obj import MetadataObj
from RSEF.metadata.api.openAlex_api_queries import pdf_title_to_meta
from ..utils.regex import (
    str_to_arxivID,
    str_to_doiID
)
import logging

log = logging.getLogger(__name__)


def extract_arxivID (openAlexJson):
    if openAlexJson is None:
        return None
    location = safe_dic(openAlexJson, "locations")
    for locat in location:
        if safe_dic(locat, "is_oa"):
            if safe_dic(locat, "pdf_url") and "arxiv" in safe_dic(locat, "pdf_url"):
                return str_to_arxivID(safe_dic(locat,"pdf_url"))


def doi_to_metadataObj(doi):
    """
    Input doi
    ------
    output
    :returns
    metadata Object
    """
    if not (doi := str_to_doiID(doi)):
        return None
    try:
        try:
            oa_meta = query_openalex_api(doi)
        except Exception as e:
            log.error(str(e))
            return None
        
        if oa_meta is None:
            log.info("No meta")
            return MetadataObj(
                title=None, doi=doi, arxiv=None, publication_date=None, authors=None
            )
        titL = safe_dic(oa_meta, "title")
        doi = str_to_doiID(safe_dic(oa_meta, "doi"))
        arxiv = extract_arxivID(oa_meta)
        publication_date = safe_dic(oa_meta, "publication_date")
        
        authorships, authors = safe_dic(oa_meta, "authorships"), []
        for author in authorships:
            authors.append(safe_dic(safe_dic(author, "author"), "display_name"))
            
        return MetadataObj(title=titL, doi=doi, arxiv=arxiv, publication_date=publication_date, authors=authors)
    except Exception as e:
        log.error(str(e))

# def title_to_meta_obj(title):
#     oa_meta = pdf_title_to_meta(title)
#     titL = safe_dic(oa_meta, "title")
#     doi = str_to_doiID(safe_dic(oa_meta, "doi"))
#     arxiv = extract_arxivID(oa_meta)
#     metadata = MetadataObj(title=titL, doi=doi, arxiv=arxiv)
#     return metadata


def doi_to_metaDict(doi):
    """
    Input doi
    ------
    output
    :returns
    Dictionary:
        K: doi
        V: metadataObj.to_dict
    """
    if not (doi:=str_to_doiID(doi)):
        return None
    mt_dict = doi_to_metadataObj(doi).to_dict()
    result = {mt_dict["doi"]: mt_dict}
    return result

def dois_to_metaDicts(list_of_dois):
    """
    Input
    List of doisdoi
    ------
    output
    :returns
    Dictionary:
        K: doi
        V: metadataObj.to_dict
    """
    result = {}
    for doi in list_of_dois:
        result.update(doi_to_metaDict(doi))
    return result


def doi_to_metaJson(doi,output_folder):
    """
    Input
    single doi
    ------
    output
    :returns
    path to JSON
    """
    meta_dict = doi_to_metaDict(doi)
    return create_meta_json(meta_dict,output_folder)


def dois_to_metaJson(doi, output_folder):
    """
    Input
    multiple dois
    ------
    output
    :returns
    path to JSON
    """
    meta_dict = dois_to_metaDicts(doi)
    return create_meta_json(meta_dict, output_folder)


def create_meta_json(meta_dict,output_folder):
    output_path = output_folder + "/" + "oa_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(meta_dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def metadataObj_to_metadataDict(metaObj):
    return {metaObj.doi: metaObj.to_dict()}


def metaDict_to_metaObj(meta_dict):
    if not meta_dict:
        return None
    title = safe_dic(meta_dict, "title")
    doi = safe_dic(meta_dict, "doi")
    arxiv = safe_dic(meta_dict, "arxiv")
    publication_date = safe_dic(meta_dict, "publication_date")
    authors = safe_dic(meta_dict, "authors")
    return MetadataObj(title=title, doi=doi, arxiv=arxiv, publication_date=publication_date, authors=authors)


def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
