from ..object_creator.implementation_url import ImplementationUrl
from ..utils.regex import str_to_doiID, str_to_arxivID
class PaperObj:
    def __init__(self, title, implementation_urls, doi, arxiv, abstract, file_name, file_path):
        self._title = title
        self._implementation_urls = implementation_urls
        self._doi = str_to_doiID(doi)
        self._arxiv = str_to_arxivID(arxiv)
        self._file_name = file_name
        self._file_path = file_path
        self._abstract = abstract

    def __str__(self):
        return f"Title: {self._title}\nImplementation URLs: {self._implementation_urls}\nDOI: {self._doi}\nArXiv: {self._arxiv}\nAbstract: {self._abstract}\nFile Name: {self._file_name}\nFile Path: {self._file_path}"

    def __repr__(self):
        return self.__str__()
    
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def implementation_urls(self):
        return self._implementation_urls

    @implementation_urls.setter
    def implementation_urls(self, value):
        self._implementation_urls = value

    def add_implementation_link(self, url, url_type, source_paragraphs=[], extraction_method='regex', frequency=1):
        if self._implementation_urls is None:
            self._implementation_urls = []
        duplicate = False
        # Look for the url in the list of implementation urls
        for implementation_url in self._implementation_urls:
            if implementation_url['url'] == url:
                # Append the extraction method to the list of extraction methods
                implementation_url['extraction_method'].append(extraction_method)
                
                # If source paragraphs are provided, append them to the list of source paragraphs
                if source_paragraphs:
                    implementation_url["source_paragraphs"].extend(source_paragraphs)
                    
                duplicate = True
                break
            
        # If the url is not in the list of implementation urls, add it
        if not duplicate:
            implementation_url = ImplementationUrl(url=url, url_type=url_type, extraction_method=[extraction_method], source_paragraphs=source_paragraphs, frequency=frequency)
            self._implementation_urls.append(implementation_url)

    @property
    def abstract(self):
        return self._abstract

    @abstract.setter
    def abstract(self, value):
        self._abstract = value

    @property
    def doi(self):
        return self._doi

    @doi.setter
    def doi(self, value):
        self._doi = value

    @property
    def arxiv(self):
        return self._arxiv

    @arxiv.setter
    def arxiv(self, value):
        self._arxiv = value

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    def to_dict(self):
        return {
            'title': self._title,
            'implementation_urls': [url for url in self._implementation_urls],
            'doi': self._doi,
            'arxiv': self._arxiv,
            'abstract': self._abstract,
            'file_name': self._file_name,
            'file_path': self._file_path
        }