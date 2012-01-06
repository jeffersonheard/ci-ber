from mongoengine import *

class Directory(Document):
    name = StringField(unique=True)
    files = ListField(StringField())
    subdirectories = ListField(StringField())
    candidates = ListField(StringField())

    meta = { 
        'indexes' : ['name']
    }


class RegularFile(Document):
    archive = StringField()
    path = StringField(unique_with=['archive'])
    filename = StringField()

    meta = {
        'indexes' : ['archive','filename','path', ('archive','path')]
    }

class Layer(EmbeddedDocument):
    name = StringField()
    feature_count = IntField()
    geography_type = StringField()
    record_type = DictField()
    bbox = ListField(FloatField())

class VectorFile(RegularFile):
    bbox = ListField(FloatField())
    srs = StringField()
    layers = ListField(EmbeddedDocumentField(Layer))

    meta = {
        'indexes' : ['archive','filename','path', ('archive','path')]
    }

class Band(EmbeddedDocument):
    datatype = StringField()
    rows = IntField()
    cols = IntField()
    metadata = DictField()
    min_val = FloatField()
    max_val = FloatField()
    missing_val = FloatField()
    color_interp = StringField()
    description = StringField()
    offset = FloatField()

class RasterFile(RegularFile):
    bbox = ListField(FloatField())
    srs = StringField()
    bands = ListField(EmbeddedDocumentField(Band))
    metadata = DictField()
    description = StringField()

    meta = {
        'indexes' : ['archive','filename','path', ('archive','path')]
    }

class DamagedRasterFile(RegularFile):
    bbox = ListField(FloatField())
    srs = StringField()
    bands = ListField(EmbeddedDocumentField(Band))
    metadata = DictField()
    description = StringField()

    meta = {
        'indexes' : ['archive','filename','path', ('archive','path')]
    }

    
