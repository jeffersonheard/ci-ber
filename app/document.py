#!/usr/local/bin/python2.7

from mongoengine import *

# record group, series, file unit, item, object

class RecordGroup(Document):
    name = StringField(unique=True, required=True)
    filepath = StringField(required=True, unique=True)
    idno = IntField(unique=True)
    bbox4326 = ListField(IntField())
    total_files = IntField(default=0)
    total_possible_rasters = IntField(default=0)
    total_possible_vectors = IntField(default=0)
    total_prepped_rasters = IntField(default=0)
    total_prepped_vectors = IntField(default=0)

RecordGroup.objects.ensure_index("+name")
RecordGroup.objects.ensure_index("+idno")

class Series(Document):
    name = StringField(unique=True, required=True)
    filepath = StringField(required=True, unique=True)
    record_group = ReferenceField(RecordGroup)
    bbox4326 = ListField(IntField())
    total_files = IntField(default=0)
    total_possible_rasters = IntField(default=0)
    total_possible_vectors = IntField(default=0)
    total_prepped_rasters = IntField(default=0)
    total_prepped_vectors = IntField(default=0)

Series.objects.ensure_index("record_group")
Series.objects.ensure_index("name")
    
class Subdirectory(Document):
    filepath = StringField(unique=True, required=True)
    record_group = ReferenceField(RecordGroup)
    series = ReferenceField(Series)
    bbox4326 = ListField(IntField())
    total_files = IntField(default=0)
    total_possible_rasters = IntField(default=0)
    total_possible_vectors = IntField(default=0)
    total_prepped_rasters = IntField(default=0)
    total_prepped_vectors = IntField(default=0)

Subdirectory.objects.ensure_index("filepath")
Subdirectory.objects.ensure_index("record_group")
Subdirectory.objects.ensure_index("series")
   
class BandMetadata(EmbeddedDocument):
    offset = FloatField()
    scale = FloatField()
    description = StringField()
    metadata = DictField()

class RasterFile(Document):
    filepath = StringField(unique=True, required=True)
    description = StringField()
    record_group = ReferenceField(RecordGroup)
    series = ReferenceField(Series)
    num_bands = IntField()
    metadata = DictField()
    band_metadata = ListField(EmbeddedDocumentField(BandMetadata))
    bbox4326 = ListField(FloatField())
    file_type = StringField()
    projection = StringField()
    rows = IntField()
    columns = IntField()

RasterFile.objects.ensure_index("+filepath")
RasterFile.objects.ensure_index("+record_group")
RasterFile.objects.ensure_index("+series")

class Layer(EmbeddedDocument):
    attribute_names = ListField(StringField())
    attribute_types = ListField(StringField())
    geometry_type = StringField()
    bbox4326 = ListField(FloatField())
    feature_count = IntField()

class VectorFile(Document):
    filepath = StringField(unique=True, required=True)
    name = StringField()
    record_group = ReferenceField(RecordGroup)
    series = ReferenceField(Series)
    attribute_names = ListField(StringField())
    layers = ListField(EmbeddedDocumentField(Layer))
    bbox4326 = ListField(FloatField())
    projection = StringField()
    file_type = StringField()

VectorFile.objects.ensure_index("+filepath")
VectorFile.objects.ensure_index("+record_group")
VectorFile.objects.ensure_index("+series")

