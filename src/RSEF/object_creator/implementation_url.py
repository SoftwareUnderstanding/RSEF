class ImplementationUrl:
    def __init__(self, url, url_type, frequency, extraction_method, source_paragraphs):
        self.url = url
        self.url_type = url_type
        self.frequency = frequency
        self.extraction_method = extraction_method
        self.source_paragraphs = source_paragraphs

    def __str__(self):
        return "URL: %s\nURL Type: %s\nFrequency: %s\nextraction_method: %s\nSource Paragraph: %s\n" % \
                (self.url, self.url_type, self.frequency, self.extraction_method, self.source_paragraphs)

    def __repr__(self):
        return self.__str__()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def url_type(self):
        return self._url_type
    
    @url_type.setter
    def url_type(self, value):
        self._url_type = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value

    @property
    def extraction_method(self):
        return self._extraction_method

    @extraction_method.setter
    def extraction_method(self, value):
        self._extraction_method = value

    @property
    def source_paragraphs(self):
        return self._source_paragraphs

    @source_paragraphs.setter
    def source_paragraphs(self, value):
        self._source_paragraphs = value

    def to_dict(self):
        return {
            "url": self.url, 
            "url_type": self.url_type,
            "frequency": self.frequency, 
            "extraction_method": self.extraction_method, 
            "source_paragraphs": self.source_paragraphs
        }

    @staticmethod
    def from_dict(dic):
        return ImplementationUrl(url=dic["url"], url_type=dic["url_type"], frequency=dic["frequency"], extraction_method=dic["extraction_method"], source_paragraphs=dic["source_paragraphs"])
