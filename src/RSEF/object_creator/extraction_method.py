class ExtractionMethod:
    def __init__(self, type, location="", location_type="", source="", source_paragraph=""):
        self._type = type
        self._location = location
        self._location_type = location_type
        self._source = source
        self._source_paragraph = source_paragraph

    def __str__(self):
        return f"type: {self._type}\nlocation: {self._location}\nlocation_type: {self._location_type}\nsource: {self._source}\nsource_paragraph: {self._source_paragraph}\n"

    def __repr__(self):
        return self.__str__()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def location_type(self):
        return self._location_type

    @location_type.setter
    def location_type(self, value):
        self._location_type = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def source_paragraph(self):
        return self._source_paragraph

    @source_paragraph.setter
    def source_paragraph(self, value):
        self._source_paragraph = value

    def to_dict(self):
        return {
            "type": self._type,
            "location": self._location,
            "location_type": self._location_type,
            "source": self._source,
            "source_paragraph": self._source_paragraph
        }

    @staticmethod
    def from_dict(dic):
        return ExtractionMethod(
            type=dic["type"],
            location=dic["location"],
            location_type=dic["location_type"],
            source=dic["source"],
            source_paragraph=dic["source_paragraph"]
        )
