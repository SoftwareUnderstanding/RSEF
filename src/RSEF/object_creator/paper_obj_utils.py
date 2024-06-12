from ..extraction.paper_obj import PaperObj

#TODO get rid of (find a cleaner solution)

def paperDict_to_paperObj(paper_dict):
    title = safe_dic(paper_dict, "title")
    doi = safe_dic(paper_dict, "doi")
    arxiv = safe_dic(paper_dict, "arxiv")
    file_name = safe_dic(paper_dict,"file_name")
    file_path = safe_dic(paper_dict,"file_path")
    urls = safe_dic(paper_dict,"implementation_urls")
    abstract = safe_dic(paper_dict,"abstract")
    return PaperObj(title=title, implementation_urls=urls, doi=doi, arxiv=arxiv, file_name=file_name, file_path=file_path, abstract=abstract)


def safe_dic(dic, key):
    try:
        return dic[key]
    except:
        return None