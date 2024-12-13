from ..utils.regex import (
    str_to_arxivID,
    str_to_doiID
)

class MetadataObj:
    def __init__(self, title, doi, arxiv):
        self._title = title
        self._doi = str_to_doiID(doi)
        self._arxiv = str_to_arxivID(arxiv)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

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

    def to_dict(self):
        return {
            'title': self._title,
            'doi': self._doi,
            'arxiv': self.arxiv,
        }
        
    def __str__(self):
        return f"Title: {self._title}, DOI: {self._doi}, Arxiv: {self._arxiv}"
