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
from ..repofrompaper.utils.constants import DOWNLOADED_PATH
from ..utils.regex import str_to_doiID, DOI_REGEX

log = logging.getLogger(__name__)

def meta_to_dwnldd(metadataObj, output_dir, pdf_link=None):
    """
    :param metdataObj: metadata object will be used to download the pdf
    :param output_dir: String output directory to where the pdf will be downloaded
    ----
    :returns
    downloaded Object, which has a filename and filepath
    """
    # takes metadata and downloads the pdf
    if not metadataObj and not pdf_link:
        return None
    
    try:
        doi = metadataObj.doi if metadataObj else None
        file_path = pdf_download_pipeline(id=doi, output_directory=output_dir, pdf_link=pdf_link)
        if not file_path:
            return None
        file_name = os.path.basename(file_path)

        return DownloadedObj(
                title=metadataObj.title if metadataObj else None,
                doi=metadataObj.doi if metadataObj else None,
                arxiv=metadataObj.arxiv if metadataObj else None,
                publication_date=metadataObj.publication_date if metadataObj else None,
                authors=metadataObj.authors if metadataObj else None,
                file_name=file_name,
                file_path=file_path,
                pdf_link=pdf_link
            )
    except Exception as e:
        try:
            meta_doi = str(metadataObj.doi) if metadataObj else None
            log.error("Error while creating the downloaded object with this doi: %s for due to %s", meta_doi, str(e))
        except Exception as e:
            log.error("Error while creating the downloaded object with this metadataObj: %s for due to %s", str(metadataObj), str(e))
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
    output_path = output_folder + DOWNLOADED_PATH
    with open(output_path, 'w+') as out_file:
        json.dump(downloaded_dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def downloadedDic_to_downloadedObj(dwnldd_dict):
    title = safe_dic(dwnldd_dict, "title")
    doi = safe_dic(dwnldd_dict, "doi")
    arxiv = safe_dic(dwnldd_dict, "arxiv")
    publication_date = safe_dic(dwnldd_dict, "publication_date")
    authors = safe_dic(dwnldd_dict, "authors")
    file_name = safe_dic(dwnldd_dict, "file_name")
    file_path = safe_dic(dwnldd_dict, "file_path")
    return DownloadedObj(title=title, doi=doi, arxiv=arxiv, publication_date=publication_date, authors=authors, file_name=file_name, file_path=file_path)


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
        log.error(str(e) + "Error while opening metadata json")
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
    output_path = output_dir + DOWNLOADED_PATH
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


def _doi_to_downloaded_obj_backup(id,output_dir):
    try:
        file_path = pdf_download_pipeline(id=id, output_directory=output_dir)
        if not file_path:
            return None
        match = re.match(DOI_REGEX, id, re.IGNORECASE)
        if match: # id is a doi
            return DownloadedObj(title=extract_pdf_title(pdf_path=file_path), doi=id, arxiv=None,
                                 publication_date=None, authors=None,
                                file_name=os.path.basename(file_path), file_path=file_path)
        else: # id is an arxiv
            return DownloadedObj(title=extract_pdf_title(pdf_path=file_path), doi=None, arxiv=id,
                                 publication_date=None, authors=None,
                                file_name=os.path.basename(file_path), file_path=file_path)
    except Exception as e:
        log.error(f"An error occurred in _doi_to_downloaded_obj_backup: {str(e)}")
        return None

def doi_to_downloadedDic(doi,output_dir):
    return downloaded_dictionary(doi_to_downloadedObj(doi, output_dir))


def dois_to_downloadedDics(dois_list, output_dir):
    result = {}
    output_path = output_dir + DOWNLOADED_PATH
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
        log.error("Error while opening the txt")
    return dois_to_downloadedDics(dois,output_dir)


def doi_to_downloadedJson(doi,output_dir):
    dict = doi_to_downloadedDic(doi, output_dir)
    output_path = output_dir + DOWNLOADED_PATH
    with open(output_path, 'w+') as out_file:
        json.dump(dict, out_file, sort_keys=True, indent=4,
                  ensure_ascii=False)
    return output_path


def dois_to_downloadedJson(dois,output_dir):
    dict = dois_to_downloadedDics(dois, output_dir)
    output_path = output_dir + DOWNLOADED_PATH
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
    publication_date = safe_dic(resp_jsn, "publication_date")
    authors = safe_dic(resp_jsn, "authors")
    return DownloadedObj(title=titL,doi=doi,arxiv=arxiv,publication_date=publication_date, authors=authors,file_name="",file_path=pdf)

# Download papers from a json containing title, doi, primary location (PDF's URL)
def json_to_downloaded_obj(json_data, output_dir):
    """
    @Param json_data path to a JSON containing title, doi, primary location (PDF's URL)
    @Param output_dir where the pdfs will be downloaded and the output JSON will be put
    -----
    :returns
    path to JSON of downloaded papers
    """
    if not os.path.exists(json_data):
        log.debug(f"JSON file '{json_data}' does not exist.")
        return None
    try:
        # Clear the content of the file downloaded_metadata.json
        downloaded_metadata_path = output_dir + DOWNLOADED_PATH
        if os.path.exists(downloaded_metadata_path):        
            with open(downloaded_metadata_path, 'w') as file:
                file.truncate(0)

        with open(json_data, 'r', encoding='utf-8') as file:
            json_data = file.read()
            if not json_data:
                log.debug(f"Error: JSON file is empty.")
                return None
            json_data_list = json.loads(json_data)
            output_path = output_dir + DOWNLOADED_PATH
            # Download the papers
            download_by_json(json_data_list, output_path)

            return output_path
    except Exception as e:
        log.error(f"Error decoding JSON data': {e}")
        return None

def download_from_doi(doi,output_dir):
    return doi_to_downloadedJson(doi,output_dir)
def download_from_doi_list(dois,output_dir):
    return dois_to_downloadedJson(dois,output_dir)
def download_from_doi_txt(dois_txt,output_dir):
    return dois_to_downloadedJson(dois_txt, output_dir)

# Download a paper from it's url
def download_from_pdf_url(url, output_dir):
    """
    @Param url URL of the paper that will be downloaded
    @Param output_dir where the pdf will be downloaded 
    -----
    :returns
    path to the folder where the pdf is downloaded
    """
    log.info(f"Download using PDF's URL: {url}")
    filename = os.path.basename(url)
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    output_path = os.path.join(output_dir, filename)
    output_path = re.sub(r'[<>:"|?*=]', '', output_path)

    if os.path.exists(output_path):
        log.info(f"File {filename} already exists in {output_dir}. Skipping download.")
        return output_path

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading PDF from {url}: {e}")
        return None

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        if content_type == 'application/pdf':
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'wb') as file:
                file.write(response.content)
            return output_path
        else:
            log.debug(f"The content at {url} is not a PDF. Content-Type is {content_type}")
            return None
    else:
        log.debug(f"Error downloading PDF from {url}: Status code {response.status_code}")
        return None

def download_by_json(json_data_list, output_path):
    """
    @Param json_data_list object containing the JSON content of the papers to download
    @Param output_dir path where the output JSON will be put
    """
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
                    downloadedObj = DownloadedObj(title=name, doi=doi, arxiv=downloadedMeta.arxiv, file_name=os.path.basename(primary_location), file_path=downloaded).to_dict()
                else:
                    downloadedObj = DownloadedObj(title=name, doi="", arxiv="", file_name=os.path.basename(primary_location), file_path=downloaded).to_dict()
                if downloadedObj:
                    save_dict_to_json(downloadedObj, output_path)
                    
        # Download using metadata
        elif doi is not None:
            log.info(f"Downloading using metadata: {doi}")
            try:
                downloadedMeta = doi_to_metadataObj(doi)
                if downloadedMeta:
                    downloadedObj = meta_to_dwnldd(downloadedMeta, ".")
                    if downloadedObj:
                        save_dict_to_json(downloadedObj.to_dict(), output_path)
                else:
                    log.debug("Couldn't find the ID in OpenAlex")
            except Exception as e:
                log.error("An error occurred while fetching metadata: ", e)

def save_dict_to_json(obj, json_path):
    """
    @Param obj object that will be saved in the JSON
    @Param json_path path to the JSON where obj will be written
    """
    json_data = []

    try:
        directory = os.path.dirname(json_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
            with open(json_path, 'r', encoding='utf-8', errors='ignore') as file:
                json_data = json.load(file)
        json_data.append(obj)
    except Exception as e:
        log.error("Error reading JSON data:", e)
    
    try:
        with open(json_path, 'w', encoding='utf-8', errors='ignore') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)

        log.info("Data successfully appended to file:", json_path)
    except Exception as e:
        log.error("Error appending JSON data to file:", e)

def remove_empty_fields_from_file(file_path):
    """
    Removes all the empty values from a JSON file.
    
    @Param file_path: path to the JSON file to process.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    
    remove_empty_fields(json_data)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

def remove_empty_fields(json_obj):
        """
        Removes all the empty values from a JSON file. 

        @Param json_obj: JSON object to process.
        """
        if isinstance(json_obj, dict):
            keys_to_delete = []
            for key, value in json_obj.items():
                if value == "" or value is None:
                    keys_to_delete.append(key)
                elif isinstance(value, (dict, list)):
                    remove_empty_fields(value)
            
            for key in keys_to_delete:
                del json_obj[key]

        elif isinstance(json_obj, list):
            for item in json_obj:
                remove_empty_fields(item)
    

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None
