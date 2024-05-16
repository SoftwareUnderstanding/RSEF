import logging
import os
import json
import re
import requests
from ..download_pdf.download_pipeline import pdf_download_pipeline
from ..download_pdf.downloaded_obj import DownloadedObj
from ..object_creator.create_metadata_obj import metaDict_to_metaObj, doi_to_metadataObj
from ..extraction.pdf_title_extraction import extract_pdf_title
from ..metadata.api.openAlex_api_queries import pdf_title_to_meta
from ..object_creator.create_metadata_obj import extract_arxivID
from ..utils.regex import str_to_doiID


def meta_to_dwnldd(metadataObj, output_dir):
    """
    :param metdataObj: metadata object will be used to download the pdf
    :param output_dir: String output directory to where the pdf will be downloaded
    ----
    :returns
    downloaded Object, which has a filename and filepath
    """
    # takes metadata and downloads the pdf
    if not metadataObj:
        return None
    try:
        file_path = pdf_download_pipeline(id=metadataObj.doi, output_directory=output_dir)
        file_name = os.path.basename(file_path)
        return DownloadedObj(title=metadataObj.title,doi=metadataObj.doi,arxiv=metadataObj.arxiv,file_name=file_name,file_path=file_path)
    except Exception as e:
        try:
            meta_doi = str(metadataObj.doi)
            logging.error("Error while creating the downloaded object with this doi: %s for due to %s", meta_doi, str(e))
        except:
            print("Error with metadataObj")
            logging.error("Error due to metadataObj")
        return None


def downloaded_dictionary(dwnldd_obj):
    """
    :param dwnldd_obj: Downloaded Object
    ----
    :returns
    Dictionary of Downloaded Dictionary
    K: is the DOI V: Dictionary of downloaded Object
    """
    if not dwnldd_obj:
        return None
    return dwnldd_obj.to_dict()

def create_downloaded_json(downloaded_dict,output_folder):
    output_path = output_folder + "/" + "downloaded_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(downloaded_dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def downloadedDic_to_downloadedObj(dwnldd_dict):
    title = safe_dic(dwnldd_dict, "title")
    doi = safe_dic(dwnldd_dict, "doi")
    arxiv = safe_dic(dwnldd_dict, "arxiv")
    file_name = safe_dic(dwnldd_dict, "file_name")
    file_path = safe_dic(dwnldd_dict, "file_path")
    return DownloadedObj(title=title, doi=doi, arxiv=arxiv, file_name=file_name, file_path=file_path)


def metaDict_to_downloaded(meta_dict, output_dir):
    '''
    @Param meta_dict metaObj as a dictionary
    @Param output_dir where the pdf will be downloaded
    ----
    :return
    downloadedObj
    '''
    meta = metaDict_to_metaObj(meta_dict)
    return meta_to_dwnldd(metadataObj=meta, output_dir=output_dir)


def metaJson_to_downloaded_dic(meta_json, output_dir):
    '''
    @Param meta_json takes json of metadata objects,
    @Param output_dir where the pdfs will be downloaded
    -----
    :returns
    Dictionary of downloaded dictionaries
    '''
    result = {}
    try:
        with open(meta_json, 'r') as f:
            metas_dict = json.load(f)
    except Exception as e:
        print(str(e) + "Error while opening metadata json")
    for doi in metas_dict:
        meta_dict = safe_dic(metas_dict,doi)
        dwnObj = metaDict_to_downloaded(meta_dict=meta_dict, output_dir= output_dir)
        result.update({dwnObj.doi: dwnObj.to_dict()})
    return result

def metaJson_to_downloadedJson(meta_json, output_dir):
    '''
    @Param meta_json takes json of metadata objects,
    @Param output_dir where the pdfs will be downloaded and the output JSON will be put
    -----
    :returns
    path to JSON of downloaded dictionaries
    '''
    dict = metaJson_to_downloaded_dic(meta_json, output_dir)
    output_path = output_dir + "/" + "downloaded_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path

def doi_to_downloadedObj(doi,output_dir):
    meta = doi_to_metadataObj(doi)
    if meta:
        return meta_to_dwnldd(meta, output_dir)
    else:
        return _doi_to_downloaded_obj_backup(doi, output_dir)


def _doi_to_downloaded_obj_backup(doi,output_dir):
    try:
        file_path = pdf_download_pipeline(id=doi, output_directory=output_dir)
        if not file_path:
            return None
        #TODO extract title
        return DownloadedObj(title=extract_pdf_title(pdf_path=file_path), doi=doi, arxiv=None,
                             file_name=os.path.basename(file_path), file_path=file_path)
    except Exception as e:
        logging.error(f"An error occurred in _doi_to_downloaded_obj_backup: {str(e)}")
        return None

def doi_to_downloadedDic(doi,output_dir):
    return downloaded_dictionary(doi_to_downloadedObj(doi, output_dir))


def dois_to_downloadedDics(dois_list, output_dir):
    result = {}
    output_path = output_dir + "/" + "downloaded_metadata.json"
    if not dois_list:
        return
    for doi in dois_list:
        if doi:
            if(dwnldd := doi_to_downloadedDic(doi, output_dir)):
                result.update(dwnldd)
                save_dict_to_json(dwnldd, output_path)
    return result

def dois_txt_to_downloadedDics(dois_txt,output_dir):
    try:
        with open(dois_txt, 'r') as file:
            dois = file.read().splitlines()
    except:
        print("Error while opening the txt")
    return dois_to_downloadedDics(dois,output_dir)


def doi_to_downloadedJson(doi,output_dir):
    dict = doi_to_downloadedDic(doi, output_dir)
    output_path = output_dir + "/" + "downloaded_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def dois_to_downloadedJson(dois,output_dir):
    dict = dois_to_downloadedDics(dois, output_dir)
    output_path = output_dir + "/" + "downloaded_metadata.json"
    with open(output_path, 'w+') as out_file:
        json.dump(dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def dois_txt_to_downloadedJson(dois_txt, output_dir):
    dois_txt_to_downloadedDics(dois_txt, output_dir)
    return output_dir

def pdf_to_downloaded_obj(pdf,output_dir):
    # TODO
    if not os.path.exists(output_dir):
        raise FileNotFoundError
    if not (title := extract_pdf_title(pdf_path=pdf)):
        return None
    resp_jsn = pdf_title_to_meta(title)
    titL = safe_dic(resp_jsn, "title")
    doi = str_to_doiID(safe_dic(resp_jsn, "doi"))
    arxiv = extract_arxivID(resp_jsn)
    return DownloadedObj(title=titL,doi=doi,arxiv=arxiv,file_name="",file_path=pdf)

# Download papers from a json containing title, doi, primary location (PDF's URL)
def json_to_downloaded_obj(json_data, output_dir):
    if not os.path.exists(json_data):
        print(f"Error: JSON file '{json_data}' does not exist.")
        return None
    try:
        # Clear the content of the file downloaded_metadata.json
        downloaded_metadata_path = os.path.join(output_dir, "downloaded_metadata.json")
        if os.path.exists(downloaded_metadata_path):        
            with open(downloaded_metadata_path, 'w') as file:
                file.truncate(0)

        with open(json_data, 'r', encoding='utf-8') as file:
            json_data = file.read()
            if not json_data:
                print(f"Error: JSON file is empty.")
                return None
            json_data_list = json.loads(json_data)
            output_path = output_dir + "/" + "downloaded_metadata.json"
            # Download the papers
            download_by_json(json_data_list, output_path)

            return output_path
    except Exception as e:
        print(f"Error decoding JSON data': {e}")
        return None

def download_from_doi(doi,output_dir):
    return doi_to_downloadedJson(doi,output_dir)
def download_from_doi_list(dois,output_dir):
    return dois_to_downloadedJson(dois,output_dir)
def download_from_doi_txt(dois_txt,output_dir):
    return dois_to_downloadedJson(dois_txt, output_dir)

# Download a paper from it's url
def download_from_pdf_url(url, output_dir):
    print(f"Download using PDF's URL: {url}")
    filename = os.path.basename(url)
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    output_path = os.path.join(output_dir, filename)
    output_path = re.sub(r'[<>:"|?*=]', '', output_path)

    if os.path.exists(output_path):
        print(f"File {filename} already exists in {output_dir}. Skipping download.")
        return output_path

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from {url}: {e}")
        print("-------------------------------")
        return None

    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'wb') as file:
            file.write(response.content)
        return output_path
    else:
        print(f"Error downloading PDF from {url}: Status code {response.status_code}")
        print("-------------------------------")
        return None

def download_by_json(json_data_list, output_path):
    for item in json_data_list:
        name = item.get("title")
        doi = item.get("doi")
        primary_location = item.get("primary_location")

        # Download using primary location
        if primary_location is not None:
            downloaded = download_from_pdf_url(primary_location, "PDFs")
            if downloaded:
                if doi is not None and doi.startswith("10."):
                    formatted_doi = 'https://doi.org/' + doi
                    downloadedMeta = doi_to_metadataObj(formatted_doi)
                    downloadedObj = DownloadedObj(name, doi, downloadedMeta.arxiv, os.path.basename(primary_location), downloaded).to_dict()
                else:
                    print("-------------------------------")
                    continue
                if downloadedObj:
                    save_dict_to_json(downloadedObj, output_path)
                    
        # Download using metadata
        elif doi is not None:
            print(f"Downloading using metadata: {doi}")
            try:
                downloadedMeta = doi_to_metadataObj(doi)
                if downloadedMeta:
                    meta_to_dwnldd(downloadedMeta, "PDFs")
                    downloadedObj = DownloadedObj(name, doi, downloadedMeta.arxiv, os.path.basename(primary_location), downloaded).to_dict()
                    if downloadedObj:
                        save_dict_to_json(downloadedObj, output_path)
                else:
                    print("Couldn't find the ID in OpenAlex")
            except Exception as e:
                print("An error occurred while fetching metadata:", e)
            print("-------------------------------")

def save_dict_to_json(obj, json_path):
    try:
        directory = os.path.dirname(json_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        json_data = []
        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
            with open(json_path, 'r', encoding='utf-8', errors='ignore') as file:
                json_data = json.load(file)

        json_data.append(obj)
    except Exception as e:
        print("Error reading JSON data:", e)
    
    try:
        with open(json_path, 'w', encoding='utf-8', errors='ignore') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)

        print("Data successfully appended to file:", json_path)
        print("-------------------------------")
    except Exception as e:
        print("Error appending JSON data to file:", e)

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
