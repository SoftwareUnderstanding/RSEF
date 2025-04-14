from ..extraction.paper_obj import PaperObj
import logging

log = logging.getLogger(__name__)
#TODO get rid of (find a cleaner solution)

def paperDict_to_paperObj(paper_dict):
    title = safe_dic(paper_dict, "title")
    doi = safe_dic(paper_dict, "doi")
    arxiv = safe_dic(paper_dict, "arxiv")
    publication_date = safe_dic(paper_dict, "publication_date")
    authors = safe_dic(paper_dict, "authors")
    file_name = safe_dic(paper_dict,"file_name")
    file_path = safe_dic(paper_dict,"file_path")
    urls = safe_dic(paper_dict,"implementation_urls")
    abstract = safe_dic(paper_dict,"abstract")
    pdf_link = safe_dic(paper_dict,"pdf_link")
    
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

def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None