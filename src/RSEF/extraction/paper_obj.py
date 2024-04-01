from ..utils.regex import str_to_doiID, str_to_arxivID

class PaperObj:
    def __init__(self, title, urls, doi, arxiv, abstract, file_name, file_path):
        self._title = title
        self._urls = urls
        self._doi = str_to_doiID(doi)
        self._arxiv = str_to_arxivID(arxiv)
        self._file_name = file_name
        self._file_path = file_path
        self._abstract = abstract

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def urls(self):
        return self._urls

    @urls.setter
    def urls(self, value):
        self._urls = value

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
            'urls': self._urls,
            'doi': self._doi,
            'arxiv': self._arxiv,
            'abstract': self._abstract,
            'file_name': self._file_name,
            'file_path': self._file_path
        }