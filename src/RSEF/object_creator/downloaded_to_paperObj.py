import json
import logging
import os

from ..object_creator.extraction_method import ExtractionMethod
from ..extraction.pdf_extraction_tika import get_possible_abstract, extract_urls, raw_read_pdf, raw_to_list
from ..extraction.paper_obj import PaperObj
from ..object_creator.create_downloadedObj import downloadedDic_to_downloadedObj, save_dict_to_json
from ..object_creator.implementation_url import ImplementationUrl

log = logging.getLogger(__name__)


def downloaded_to_paperObj(downloadedObj, paper_meta=None):
    """
    :param: downloadedObj
    ---
    :returns:
    Paper Obj (will have processed the paper within the downloaded Obj to look for github urls)
    """
    if not downloadedObj and not paper_meta:
        return
    elif not downloadedObj and paper_meta:
        title = paper_meta.title if paper_meta else None
        doi = paper_meta.doi if paper_meta else None
        arxiv = paper_meta.arxiv if paper_meta else None
        publication_date = paper_meta.publication_date if paper_meta else None
        authors = paper_meta.authors if paper_meta else None


        return PaperObj(
            title=title,
            doi=doi,
            arxiv=arxiv,
            publication_date=publication_date,
            authors=authors,
            file_name=None,
            file_path=None,
            implementation_urls=[],
            abstract=None
        )

    try:
        # TODO optimise
        raw_pdf_data = raw_read_pdf(pdf_path=downloadedObj.file_path)
        pdf_data_list = raw_to_list(raw_pdf_data)
        urls_dict, urls = extract_urls(raw_pdf_data, pdf_data_list), []
        if urls_dict:
            for url_type, url_list in urls_dict.items():
                for url in url_list:
                    extraction_method = ExtractionMethod(
                        type="regex", location="", location_type="", source="", source_paragraph="")
                    implementation_url = ImplementationUrl(identifier=url['url'], type=url_type, paper_frequency=url['#_appearances'], extraction_methods=[extraction_method]
                                                           )
                    urls.append(implementation_url.to_dict())
        abstract = get_possible_abstract(pdf_data_list)
        title = downloadedObj.title
        doi = downloadedObj.doi
        arxiv = downloadedObj.arxiv
        publication_date = downloadedObj.publication_date
        authors = downloadedObj.authors
        file_name = downloadedObj.file_name
        file_path = downloadedObj.file_path
        pdf_link = downloadedObj.pdf_link
        return PaperObj(
            title=title,
            implementation_urls=urls,
            doi=doi,
            arxiv=arxiv,
            abstract=abstract,
            publication_date=publication_date,
            authors=authors,
            file_name=file_name,
            file_path=file_path,
            pdf_link=pdf_link
        )
    except Exception as e:
        log.error("Error while trying to read from the pdf: ", str(e))


def dwnldd_obj_to_paper_dic(downloaded_obj):
    paper = downloaded_to_paperObj(downloaded_obj)
    return paperObj_ppDict(paper=paper)


def dwnldd_obj_to_paper_json(download_obj, output_dir):
    pp_dic = dwnldd_obj_to_paper_dic(download_obj)
    return pp_dic_to_json(pp_dic, output_dir)


def dwnlddDic_to_paper_dic(downloadeds_dic, output_path):
    count = 0
    for index, obj in enumerate(downloadeds_dic):
        dwnObj = downloadedDic_to_downloadedObj(obj)
        paper = downloaded_to_paperObj(dwnObj)
        count += 1
        log.info(f"Processed {index}, Total Processed: {count} Papers")
        save_dict_to_json(paper.to_dict(), output_path)
    return output_path


def dwnlddDic_to_paperJson(downloadeds_dic, output_dir):
    pp_dic = dwnlddDic_to_paper_dic(downloadeds_dic)
    return pp_dic_to_json(pp_dic, output_dir)


def dwnlddJson_to_paper_dic(dwnldd_json, output_dir):
    """
    @Param dwnldd_json Json of the downloaded Objects
    ----
    :returns
    dictionary of paper dictionaries
    """
    try:
        with open(dwnldd_json, 'r', encoding='utf-8', errors='ignore') as f:
            dwnldd_json = json.load(f)
    except Exception as e:
        print(str(e) + "Error while opening metadata json")
    output_path = os.path.join(output_dir, "processed_metadata.json")
    return dwnlddDic_to_paper_dic(dwnldd_json, output_path)


def dwnlddJson_to_paperJson(dwnldd_json, output_dir):
    """
    @Param dwnldd_json: Json of Downloaded Dictionaries
    @Param output_dir: Directory to put the output JSON
    :return
    Path to the paper JSON
    """
    dwnlddJson_to_paper_dic(dwnldd_json, output_dir)
    return output_dir


def pp_dic_to_json(pp_dic, output_dir):
    """
    @Param pp_dic: is a paper dictionary
    @Param output_dir where the JSON will be saved
    --
    :return
    Path to the json
    """
    output_path = os.path.join(output_dir, "processed_metadata.json")
    with open(output_path, 'w+') as out_file:
        json.dump(pp_dic, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


# TODO cleanup all
BACKUP_ID = 0


def paperObj_ppDict(paper):
    # TODO find a cleaner way
    global BACKUP_ID
    try:
        if paper is not None:
            if paper.doi is None:
                log.warning(
                    f"This paper does not have a doi, created a fake ID for {paper.title}")
                paper.doi = BACKUP_ID
                ans = {str(BACKUP_ID): paper.to_dict()}
                BACKUP_ID += 1
                return ans
            return {paper.doi: paper.to_dict()}
        else:
            log.info("paper is None; cannot process.")
            return None
    except Exception as e:
        log.error(
            "An error occurred while processing paper with DOI %s: %s", paper.doi, str(e))


def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
