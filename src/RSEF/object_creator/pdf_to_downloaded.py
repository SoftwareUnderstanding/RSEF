
from ..utils.regex import adrian_is_filename_doi, adrian_filename_to_doi_convert
from ..metadata.api.openAlex_api_queries import query_openalex_api
from ..utils.regex import str_to_arxivID, str_to_doiID
from ..download_pdf.downloaded_obj import DownloadedObj
#TODO CHANGE NAME OF CREATE_DOWNLOADED_OBJ
from ..object_creator.create_downloadedObj import downloaded_dictionary
import os.path
import json

from .create_metadata_obj import doi_to_metadataObj


#WARNING this is for adrians pdfs
#if you dont know who adrian is this script is not of interest

def extract_arxivID (openAlexJson):
    location = safe_dic(openAlexJson, "locations")
    for locat in location:
        if safe_dic(locat, "is_oa") == True:
            if safe_dic(locat, "pdf_url") and "arxiv" in safe_dic(locat, "pdf_url"):
                return str_to_arxivID(safe_dic(locat,"pdf_url"))


def pdfDoi_to_downloaded(doi,file_path):
    try:
        try:
            oa_meta = query_openalex_api(doi)
        except Exception as e:
            print(str(e))
        if oa_meta is None:
            print("No meta")
        titL = safe_dic(oa_meta, "title")
        doi = str_to_doiID(safe_dic(oa_meta, "doi"))
        arxiv = extract_arxivID(oa_meta)
        file_name = os.path.basename(file_path)
        publication_date = safe_dic(oa_meta, "publication_date")
        
        authorships, authors = safe_dic(oa_meta, "authorships"), []
        for author in authorships:
            authors.append(safe_dic(safe_dic(author, "author"), "display_name"))

        pdf_link = safe_dic(oa_meta, "primary_location")["pdf_url"]
            
        return DownloadedObj(titL, doi, arxiv, publication_date, authors, file_name, file_path, pdf_link)
    except Exception as e:
        print(str(e))


def adrian_to_downloaded(file_path):
    '''
    Uses Adrians File naming system.
    arxiv are as is
    doi's have the following replaced: "/" for a "_"
    '''
    file_name = os.path.basename(file_path)
    possible_ID = file_name.replace(".pdf", "")
    if str_to_arxivID(possible_ID):
        #TODO
        pass
    possible_ID = possible_ID.replace("_","/")
    if (doi:= adrian_is_filename_doi(possible_ID)):
        return pdfDoi_to_downloaded(doi,file_path)

def adrian_pdfs_2dictionary(directory):
    result = {}
    num_pdfs = 0
    try:
        list = os.listdir(directory)
    except Exception as e:
        print(str(e))
        return None
    for file in list:
        file_path = os.path.join(directory,file)
        dwnldd = adrian_to_downloaded(file_path)
        if dwnldd:
            result.update(downloaded_dictionary(dwnldd))
            num_pdfs += 1
            print("Number of pdfs/downloaded Objects made = " + str(num_pdfs))
    return result

def adrian_pdfs_2Json(directory):
    dictJson = adrian_pdfs_2dictionary(directory)
    if not dictJson:
        return None
    output_path = directory + "/" +  "pdf_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(dictJson, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path
def pdfs_to_downloaded_Json(directory):
    dictJson = pdfs_to_downloaded_dics(directory)
    if not dictJson:
        return None
    output_path = directory + "/" + "pdf_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(dictJson, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path
def pdfs_to_downloaded_dics(directory):
    result = {}
    num_pdfs = 0
    try:
        list = os.listdir(directory)
    except Exception as e:
        print(str(e))
        return None
    for file in list:
        file_path = os.path.join(directory,file)
        dwnldd = pdf_to_downloaded_dic(file_path)
        if dwnldd:
            result.update(dwnldd)
            num_pdfs += 1
            print("Number of pdfs/downloaded Objects made = " + str(num_pdfs))
    return result

def pdf_to_downloaded_dic(file_path):
    file_name = os.path.basename(file_path)
    doi = adrian_filename_to_doi_convert(file_name)
    meta = doi_to_metadataObj(doi)
    if not meta:
        return None
    return {doi:{
    'title': meta.title,
    'doi': meta.doi,
    'arxiv': meta.arxiv,
    'file_name': file_name,
    'file_path': file_path
    }}

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None


