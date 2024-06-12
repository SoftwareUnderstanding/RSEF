class ImplementationUrl:
    def __init__(self, identifier, type, paper_frequency, extraction_methods):
        self.identifier = identifier
        self.type = type
        self.paper_frequency = paper_frequency
        self.extraction_methods = extraction_methods if extraction_methods is not None else []

    def __str__(self):
        return "URL: %s\nURL Type: %s\nFrequency: %s\nExtraction Methods: %s\n" % \
                (self.identifier, self.type, self.paper_frequency, self.extraction_methods)

    def __repr__(self):
        return self.__str__()

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def paper_frequency(self):
        return self._paper_frequency

    @paper_frequency.setter
    def paper_frequency(self, value):
        self._paper_frequency = value

    @property
    def extraction_methods(self):
        return self._extraction_methods

    @extraction_methods.setter
    def extraction_methods(self, value):
        self._extraction_methods = value

    def to_dict(self):
        return {
            "identifier": self.identifier,
            "type": self.type,
            "paper_frequency": self.paper_frequency,
            "extraction_methods": [em for em in self.extraction_methods] 
        }

    @staticmethod
    def from_dict(dic):
        return ImplementationUrl(
            identifier=dic["identifier"],
            type=dic["type"],
            paper_frequency=dic["paper_frequency"],
            extraction_methods=dic["extraction_methods"]
        )
