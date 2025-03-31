
from ..utils.regex import (
    str_to_arxivID,
    str_to_doiID
)


class DownloadedObj:

    def __init__(self, title, doi, arxiv, publication_date, authors, file_name, file_path, pdf_link=None):
        self._title = title
        self._doi = str_to_doiID(doi)
        self._arxiv = str_to_arxivID(arxiv)
        self._publication_date = publication_date
        self._authors = authors
        self._file_name = file_name
        self._file_path = file_path
        self._pdf_link = pdf_link

    def __str__(self):
        return f"Title: {self._title}\nDOI: {self._doi}\nArXiv: {self._arxiv}\n\
                    Publication Date: {self._publication_date}\nAuthors: {self._authors}\n\
                        File Name: {self._file_name}\nFile Path: {self._file_path}\nPDF Link: {self._pdf_link}"

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
        
    @property
    def pdf_link(self):
        return self._pdf_link
    
    @pdf_link.setter
    def pdf_link(self, value):
        self._pdf_link = value

    def to_dict(self):
        return {
            'title': self._title,
            'doi': self._doi,
            'arxiv': self.arxiv,
            'publication_date': self._publication_date,
            'authors': ", ".join(self._authors) if self._authors else "",
            'file_name': self._file_name,
            'file_path': self._file_path,
            'pdf_link': self._pdf_link
        }
