from ..object_creator.implementation_url import ImplementationUrl
from ..utils.regex import str_to_doiID, str_to_arxivID

class PaperObj:
    def __init__(self, title, implementation_urls, doi, arxiv, abstract, file_name, file_path):
        self._title = title
        self._implementation_urls = [ImplementationUrl.from_dict(url) for url in implementation_urls]
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
        self._implementation_urls = [ImplementationUrl.from_dict(url) for url in value]

    def add_implementation_link(self, url, url_type, extraction_method, frequency=1):
        if self._implementation_urls is None:
            self._implementation_urls = []
        duplicate = False
        # Look for the url in the list of implementation urls
        for implementation_url in self._implementation_urls:
            if implementation_url.identifier == url:
                implementation_url.extraction_methods.append(extraction_method.to_dict())
                duplicate = True
                break
        if not duplicate:
            new_url = ImplementationUrl(
                identifier=url,
                type=url_type,
                paper_frequency=frequency,
                extraction_methods=[extraction_method]
            )
            self._implementation_urls.append(new_url)

    def remove_regex(self):
        try:
            self._implementation_urls = [
                url for url in self._implementation_urls if not self.has_only_regex(url)
            ]
        except Exception as e:
            print(f"An error occurred in remove_regex: {e}")
        
    def has_only_regex(self, implementation_url):
        try:
            return all(method['type'] == 'regex' for method in implementation_url.extraction_methods)
        except Exception as e:
            print(f"An error occurred in _has_only_regex: {e}")
            return False

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
            'implementation_urls': [url.to_dict() for url in self._implementation_urls],
            'doi': self._doi,
            'arxiv': self._arxiv,
            'abstract': self._abstract,
            'file_name': self._file_name,
            'file_path': self._file_path
        }