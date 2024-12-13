from ..object_creator.extraction_method import ExtractionMethod
from .create_metadata_obj import doi_to_metadataObj
from .create_downloadedObj import meta_to_dwnldd, pdf_to_downloaded_obj, remove_empty_fields_from_file, save_dict_to_json
from .downloaded_to_paperObj import downloaded_to_paperObj
from .paper_to_directionality import check_bidir, check_unidir
from .paper_obj_utils import paperDict_to_paperObj
from ..repofrompaper.rfp import extract_repo_links_from_pdf
from ..extraction.paper_obj import PaperObj
import logging
import json
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def doi_to_paper(doi, output_dir):
    """
    :param doi: doi
    :param output_dir: where the pdf will be downloaded to
    :returns:
    paperObj
    """
    meta = doi_to_metadataObj(doi)
    downldd = meta_to_dwnldd(meta, output_dir)
    paper = downloaded_to_paperObj(downldd)
    return paper


def pdf_to_paper(pdf, output_dir):
    """
    :param pdf: path to pdf file
    :param output_dir: output directory
    :returns:
    paperObj from pdf
    """
    # TODO
    dwnldd = pdf_to_downloaded_obj(pdf, output_dir)
    return downloaded_to_paperObj(downloadedObj=dwnldd)


def process_paper(paper: PaperObj, output_dir, bidir=True, unidir=True):
    """
    :param paper: paperObj
    :param output_dir: output directory
    :param bidir: flag to enable bidirectional pipeline
    :param unidir: flag to enable unidirectional pipeline
    :returns:
    paperObj with URLs found based on the specified pipeline types
    """
    if paper.doi or paper.arxiv:
        if not paper.implementation_urls:
            log.info("No implementation URLs present in the paper object!")
            return paper
        
        if bidir:
            try:
                log.info("Checking bidirectional links")
                paper = check_bidir(paper, output_dir)
                
            except Exception as e:
                log.error("Error extracting bidirectional relationship" + str(e))

        if unidir:
            try:
                log.info("Checking unidirectional links")
                
                repo_link, source_para = extract_repo_links_from_pdf(
                    paper.file_path)
                
                if repo_link:
                    extraction_method = ExtractionMethod(
                        type='unidir', location=paper.file_path, location_type='PAPER', source_paragraph=source_para)
                    paper.add_implementation_link(
                        repo_link, 'git', extraction_method=extraction_method)
                    
            except Exception as e:
                log.error(
                    "Error extracting unidirectional relationship: " + str(e))

    # Clean up the paper object
    paper.remove_duplicated_extraction_methods()
    paper.remove_regex()

    return paper


def single_doi_pipeline(doi, output_dir, bidir=True, unidir=True):
    """
    :param doi: DOI
    :param output_dir: where the PDFs will be downloaded to
    :param bidir: flag to enable bidirectional pipeline
    :param unidir: flag to enable unidirectional pipeline
    :returns:
    dictionary with DOI and the URLs found based on the specified pipeline types
    """
    paper = doi_to_paper(doi, output_dir)

    if not paper:
        return None

    paper = process_paper(paper, output_dir, bidir=bidir, unidir=unidir)
    result = [paper.to_dict()]

    return dict_to_json({'RSEF Output': result}, output_path=os.path.join(output_dir, "url_search_output.json"))


# TODO: Check if this function is needed, it is not used in the code
def single_pdf_pipeline_single_bidir(pdf, output_dir):
    """
    :param pdf: pdf
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are bidirectional for that doi
    """
    paper = pdf_to_paper(pdf, output_dir)
    if not paper:
        log.error("Error while creating paperObj")
        return None
    result = check_bidir(paper, output_dir)
    return result


# TODO: Check if this function is needed, it is not used in the code
def single_pdf_pipeline_unidir(pdf, output_dir):
    """
    :param pdf: pdf
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are unidirectional for that doi
    """
    paper = pdf_to_paper(pdf, output_dir)
    if not paper:
        log.error("Error while creating paperObj")
        return None
    result = check_unidir(paper, output_dir)
    return result


def multi_doi_pipeline(list_dois, output_dir, bidir=True, unidir=True):
    """
    :param list_dois: list of DOIs
    :param output_dir: where the PDFs will be downloaded to
    :param bidir: flag to enable bidirectional search
    :param unidir: flag to enable unidirectional search
    :returns:
    dictionary with DOIs and the URLs found based on the specified search type
    """
    result = []

    for doi in list_dois:
        log.info(f"Analyzing DOI: {doi}")
        try:
            paper = doi_to_paper(doi, output_dir)

            if not paper:
                log.debug("Error while creating paperObj")
                continue

            paper = process_paper(
                paper, output_dir, bidir=bidir, unidir=unidir)

            result.append(paper.to_dict())
        except Exception as e:
            log.error(f"Error while processing {doi}")
            log.error(str(e))
        finally:
            log.info(f"Finished analyzing DOI: {doi}")
            print("-------------------------------\n")

    return dict_to_json({'RSEF Output': result}, output_path=os.path.join(output_dir, "url_search_output.json"))


def multi_doi_search(dois_txt, output_dir, bidir=True, unidir=True):
    """
    :param dois_txt: DOIs separated by \n within a txt file
    :param output_dir: where the PDFs will be downloaded to
    :param bidir: flag to enable bidirectional search
    :param unidir: flag to enable unidirectional search
    :returns:
    dictionary with DOIs and the URLs found based on the specified search type
    """
    try:
        with open(dois_txt, 'r') as file:
            dois = file.read().splitlines()
    except:
        log.error("Error while opening the txt")
        return None

    return multi_doi_pipeline(dois, output_dir, bidir=bidir, unidir=unidir)


def dict_to_json(dictionary, output_path):
    """
    :param dictionary: dictionary to be turned to a json
    :returns:
    path to output JSON
    """
    try:
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(output_path, 'w+', encoding='utf-8') as out_file:
            json.dump(dictionary, out_file, indent=4, ensure_ascii=False)
        return output_path
    except Exception as e:
        log.error("Error while trying to save the JSON")
        log.error(str(e))
        return None


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def paper_objects_search(papers_json, output_dir, bidir=True, unidir=True):
    """
    :param papers_json: JSON of paperObj (as a dictionary)
    :param output_dir: where the JSON will be saved to
    :param bidir: flag to enable bidirectional search
    :param unidir: flag to enable unidirectional search
    :returns:
    path to output JSON
    """
    file_path = os.path.join(output_dir, "url_search_output.json")

    try:
        with open(papers_json, 'r', encoding='utf-8', errors='ignore') as f:
            paper_dicts = json.load(f)
        log.info("Successfully opened JSON")
    except Exception as e:
        log.error("Error while trying to load the Papers JSON")
        log.error(str(e))
        return

    for obj in paper_dicts:
        if obj['doi']:
            log.info(f"Analyzing directionality for {obj['doi']}")
        elif obj['arxiv']:
            log.info(f"Analyzing directionality for {obj['arxiv']}")
        paper = paperDict_to_paperObj(obj)

        if not paper:
            log.error("Error while creating paperObj")
            return None

        paper = process_paper(paper, output_dir, bidir=bidir, unidir=unidir)

        try:
            paper_dict = paper.to_dict()
            save_dict_to_json(paper_dict, file_path)
        except Exception as e:
            log.error(
                f"Error while converting paperObj to dict for {obj['doi']}: {e}")
            continue

    try:
        remove_empty_fields_from_file(file_path)
    except Exception as e:
        log.error(f"Error while deleting the empty values from JSON: {e}")

    return file_path


def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
