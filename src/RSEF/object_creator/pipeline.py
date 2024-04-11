# TODO
from .create_metadata_obj import doi_to_metadataObj
from .create_downloadedObj import meta_to_dwnldd, pdf_to_downloaded_obj
from .downloaded_to_paperObj import downloaded_to_paperObj
from .paper_to_directionality import check_bidir, check_unidir
from .paper_obj_utils import paperDict_to_paperObj
from ..repofrompaper.rfp import extract_repo_links_from_pdf
import json
import os


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


def single_doi_pipeline_bidir(doi, output_dir):
    """
    :param doi: doi
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are bidirectional for that doi
    """
    paper = doi_to_paper(doi,output_dir)
    return check_bidir(paper,output_dir)


def single_doi_pipeline_unidir(doi, output_dir):
    """
    :param doi: doi
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are unidirectional for that doi
    """
    paper = doi_to_paper(doi, output_dir)
    if not paper:
        print("Error while creating paperObj")
        return None
    repo_link, source_para = extract_repo_links_from_pdf(paper.file_path)
    if repo_link:
        paper.add_implementation_link(repo_link, 'git', source_paragraphs=[source_para], extraction_method='unidir')
    return paper


def single_pdf_pipeline_single_bidir(pdf, output_dir):
    """
    :param pdf: pdf
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are bidirectional for that doi
    """
    paper = pdf_to_paper(pdf,output_dir)
    if not paper:
        print("Error while creating paperObj")
        return None
    result = check_bidir(paper,output_dir)
    return result


def single_pdf_pipeline_unidir(pdf, output_dir):
    """
    :param pdf: pdf
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with doi and the urls found that are unidirectional for that doi
    """
    paper = pdf_to_paper(pdf,output_dir)
    if not paper:
        print("Error while creating paperObj")
        return None
    result = check_unidir(paper,output_dir)
    return result


def multiple_doi_pipeline_bidir(list_dois, output_dir):
    """
    :param list_dois: list of dois
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with dois and the urls found that are bidirectional for that doi
    """
    result = {}
    try:
        for doi in list_dois:
            paper = doi_to_paper(doi,output_dir)
            if not paper:
                continue
            if (bidir := (check_bidir(paper, output_dir))):
                result.update(bidir)
        return result
    except Exception as e:
        print(str(e))
        return None


def multiple_doi_pipeline_unidir(list_dois, output_dir):
    """
    :param list_dois: list of dois
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with dois and the urls found that are unidirectional for that doi
    """
    result = {}
    try:
        for doi in list_dois:
            paper = doi_to_paper(doi,output_dir)
            if not paper:
                continue
            if (unidir:=(check_unidir(paper,output_dir))):
                result.update(unidir)
        return result
    except Exception as e:
        print(str(e))
        return None


def dois_txt_pipeline_bidir(dois_txt, output_dir):
    """
    :param dois_txt: dois seperated by \n within a txt
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with dois and the urls found that are bidirectional for that doi
    """
    try:
        with open(dois_txt, 'r') as file:
            dois = file.read().splitlines()
    except:
        print("Error while opening the txt")
    return multiple_doi_pipeline_bidir(dois, output_dir)


def dois_txt_pipeline_unidir(dois_txt, output_dir):
    """
    :param dois_txt: dois seperated by \n within a txt
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with dois and the urls found that are bidirectional for that doi
    """
    try:
        with open(dois_txt, 'r') as file:
            dois = file.read().splitlines()
    except:
        print("Error while opening the txt")
    return multiple_doi_pipeline_unidir(dois, output_dir)


def dict_to_json(dictionary, output_path):
    """
    :param dictionary: dictionary to be turned to a json
    :returns:
    path to output JSON
    """
    try:
        with open(output_path, 'w+') as out_file:
            json.dump(dictionary, out_file, indent=4, ensure_ascii=False)
        return output_path
    except Exception as e:
        print(str(e))
        return None


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def dois_txt_to_bidir_json(dois_txt, output_dir):
    """
    :param dois_txt: dois seperated by \n within a txt
    :param output_dir: where the pdf will be downloaded to
    :returns:
    path to output JSON
    """
    output_path = os.path.join(output_dir, "bidir_1.json")
    return dict_to_json(dois_txt_pipeline_bidir(dois_txt, output_dir), output_path)


def dois_txt_to_unidir_json(dois_txt, output_dir):
    """
    :param dois_txt: dois seperated by \n within a txt
    :param output_dir: where the pdf will be downloaded to
    :returns:
    path to output JSON
    """
    output_path = os.path.join(output_dir,"unidir.json")
    return dict_to_json(dois_txt_pipeline_unidir(dois_txt, output_dir), output_path)


def papers_json_to_unidir_json(papers_json, output_dir):
    """
    :param papers_json: Json of papers K:doi V: paperObj
    :param output_dir: where the pdf will be downloaded to
    :returns:
    dictionary with dois and the urls found that are unidirectional for that doi
    """
    result = {}
    try:
        paper_dicts = load_json(papers_json)
        print("Successfully opened JSON")
    except Exception as e:
        print("Error while trying to load the Papers JSON")
        print(str(e))
        return None
    for id in paper_dicts:
        print(f"Analysing directionality for {id}")
        paperDict = safe_dic(paper_dicts, id)
        paper = paperDict_to_paperObj(paperDict)
        unidir = check_unidir(paper, output_dir)
        if unidir:
            result.update(unidir)
        print(f"Finished analysing {id}")
        print(f"Unidirectional?", (unidir is not None))
        print("=========================")
    return dict_to_json(result, output_path=os.path.join(output_dir, "unidir.json"))


def papers_json_to_bidir_json(papers_json, output_dir):
    """
    :param papers_json: json of papers, Key: DOI, V: paperObj (as a dictionary)
    :param output_dir: where the json will be saved to
    :returns:
    path to output JSON
    """
    result = {}
    try:
        paper_dicts = load_json(papers_json)
        print("Successfully opened JSON")
    except Exception as e:
        print("Error while trying to load the Papers JSON")
        print(str(e))
        return None
    for id in paper_dicts:
        print(f"Analysing directionality for {id}")
        paperDict = safe_dic(paper_dicts, id)
        paper = paperDict_to_paperObj(paperDict)
        bidir = check_bidir(paper, output_dir)
        if bidir:
            result.update(bidir)
        print(f"Finished analysing {id}")
        print(f"Bidirectional?", (bidir is not None))
        print("=========================")
    return dict_to_json(result, output_path=os.path.join(output_dir, "bidir.json"))


def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
