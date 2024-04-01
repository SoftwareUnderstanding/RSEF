import json
import logging
import os
from ..extraction.pdf_extraction_tika import read_pdf_list, get_possible_abstract, extract_urls, raw_read_pdf, raw_to_list
from ..extraction.paper_obj import PaperObj
from ..object_creator.create_downloadedObj import downloadedDic_to_downloadedObj


def downloaded_to_paperObj(downloadedObj):
    """
    :param: downloadedObj
    ---
    :returns:
    Paper Obj (will have processed the paper within the downloaded Obj to look for github urls)
    """
    if not downloadedObj:
        return None
    try:
        # TODO optimise
        raw_pdf_data = raw_read_pdf(pdf_path=downloadedObj.file_path)
        pdf_data_list = raw_to_list(raw_pdf_data)
        urls = extract_urls(raw_pdf_data, pdf_data_list)
        abstract = get_possible_abstract(pdf_data_list)
        title = downloadedObj.title
        doi = downloadedObj.doi
        arxiv = downloadedObj.arxiv
        file_name = downloadedObj.file_name
        file_path = downloadedObj.file_path
        return PaperObj(title=title, urls=urls, doi=doi, arxiv=arxiv, abstract=abstract, file_name=file_name, file_path=file_path)
    except Exception as e:
        print(str(e))
        print("Error while trying to read from the pdf")


def dwnldd_obj_to_paper_dic(downloaded_obj):
    paper = downloaded_to_paperObj(downloaded_obj)
    return paperObj_ppDict(paper=paper)


def dwnldd_obj_to_paper_json(download_obj,output_dir):
    pp_dic = dwnldd_obj_to_paper_dic(download_obj)
    return pp_dic_to_json(pp_dic, output_dir)


def dwnlddDic_to_paper_dic(downloadeds_dic):
    result = {}
    count = 0
    for iden in downloadeds_dic:
        dwnldd_dict = safe_dic(downloadeds_dic, iden)
        dwnObj = downloadedDic_to_downloadedObj(dwnldd_dict=dwnldd_dict)
        paper = downloaded_to_paperObj(dwnObj)
        result.update({iden: paper.to_dict()})
        print(iden)
        count += 1
        print("Processed %s, \n Total Processed: %s Papers" % (iden, count))
    return result


def dwnlddDic_to_paperJson(downloadeds_dic,output_dir):
    pp_dic = dwnlddDic_to_paper_dic(downloadeds_dic)
    return pp_dic_to_json(pp_dic,output_dir)


def dwnlddJson_to_paper_dic(dwnldd_json):
    """
    @Param dwnldd_json Json of the downloaded Objects
    ----
    :returns
    dictionary of paper dictionaries
    """
    result = {}
    try:
        with open(dwnldd_json, 'r') as f:
            dwnldd_json = json.load(f)
    except Exception as e:
        print(str(e) + "Error while opening metadata json")
    return dwnlddDic_to_paper_dic(downloadeds_dic=dwnldd_json)


def dwnlddJson_to_paperJson(dwnldd_json, output_dir):
    """
    @Param dwnldd_json: Json of Downloaded Dictionaries
    @Param output_dir: Directory to put the output JSON
    :return
    Path to the paper JSON
    """
    pp_dic = dwnlddJson_to_paper_dic(dwnldd_json)
    return pp_dic_to_json(pp_dic, output_dir)


def pp_dic_to_json(pp_dic, output_dir):
    """
    @Param pp_dic: is a paper dictionary
    @Param output_dir where the JSON will be saved
    --
    :return
    Path to the json
    """
    output_path = os.path.join(output_dir,"processed_metadata.json")
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
                logging.warning(f"This paper does not have a doi, created a fake ID for {paper.title}")
                paper.doi = BACKUP_ID
                ans = {str(BACKUP_ID): paper.to_dict()}
                BACKUP_ID += 1
                return ans
            return {paper.doi: paper.to_dict()}
        else:
            logging.error("paper is None; cannot process.")
            return None
    except Exception as e:
        logging.error("An error occurred while processing paper with DOI %s: %s", paper.doi, str(e))

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None

