from ..utils.regex import (
    str_to_arxivID,
    str_to_doiID
)

class MetadataObj:
    def __init__(self, title, doi, arxiv, publication_date=None, authors: list=None):
        self._title = title
        self._doi = str_to_doiID(doi)
        self._arxiv = str_to_arxivID(arxiv)
        self.authors = authors
        self.publication_date = publication_date

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
        
    @property
    def publication_date(self):
        return self._publication_date
    
    @publication_date.setter
    def publication_date(self, value):
        self._publication_date = value
        
    @property
    def authors(self):
        return self._authors
    
    @authors.setter
    def authors(self, value):
        self._authors = value

    def to_dict(self):
        return {
            'title': self._title,
            'doi': self._doi,
            'arxiv': self.arxiv,
            'publication_date': self.publication_date,
            'authors': self.authors
        }
        
    def __str__(self):
        authors_str = ", ".join(self.authors) if self.authors else ""
        return f"Title: {self._title}, DOI: {self._doi}, Arxiv: {self._arxiv}, Authors: {authors_str}, Publication Date: {self.publication_date}"
