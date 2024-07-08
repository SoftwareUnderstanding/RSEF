from ..object_creator.implementation_url import ImplementationUrl
from ..utils.regex import str_to_doiID, str_to_arxivID


class PaperObj:
    def __init__(self, title, implementation_urls, doi, arxiv, abstract, file_name, file_path):
        self._title: str = title
        self._implementation_urls: list[ImplementationUrl] = [
            ImplementationUrl.from_dict(url) for url in implementation_urls]
        self._doi: str = str_to_doiID(doi)
        self._arxiv: str = str_to_arxivID(arxiv)
        self._file_name: str = file_name
        self._file_path: str = file_path
        self._abstract: str = abstract

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
        self._implementation_urls = [
            ImplementationUrl.from_dict(url) for url in value]

    def add_implementation_link(self, url, url_type, extraction_method, frequency=1):
        if self._implementation_urls is None:
            self._implementation_urls = []
        duplicate = False
        # Look for the url in the list of implementation urls
        for implementation_url in self._implementation_urls:
            if implementation_url.identifier == url:
                implementation_url.extraction_methods.append(extraction_method)
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
        filtered_urls = []
        try:
            for url in self._implementation_urls:
                url.extraction_methods = [
                    method for method in url.extraction_methods if method.type != 'regex'
                ]
                # Add the URL to filtered_urls if it has non-empty extraction methods
                if url.extraction_methods:
                    filtered_urls.append(url)

            # Update _implementation_urls to only include URLs with non-empty extraction methods
            self._implementation_urls = filtered_urls
        except Exception as e:
            print(f"An error occurred in remove_regex: {e}")

    def remove_duplicated_extraction_methods(self):
        filtered_urls = []
        try:
            for url in self._implementation_urls:
                seen_locations = set()
                unique_methods = []
                has_citation_file = False
                citation_file_location_type = None
                cff_location_type = None

                for method in url.extraction_methods:
                    if method.location == 'CITATION_FILE':
                        unique_methods.append(method)
                        has_citation_file = True
                        citation_file_location_type = method.location_type
                    elif method.location == 'FILE_CFF':
                        cff_location_type = method.location_type
                    elif method.location not in seen_locations:
                        seen_locations.add(method.location)
                        unique_methods.append(method)

                for method in unique_methods:
                    if method.location == 'FILE_CFF' and has_citation_file:
                        unique_methods.remove(method)
                    if method.location == 'CITATION_FILE' and citation_file_location_type != cff_location_type:
                        method.location_type(
                            f"{citation_file_location_type} , {cff_location_type}")
                url.extraction_methods = unique_methods

                if url.extraction_methods:
                    filtered_urls.append(url)

            self._implementation_urls = filtered_urls

        except Exception as e:
            print(
                f"An error occurred in remove_duplicated_extraction_methods: {e}")

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
