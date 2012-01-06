#!/usr/local/bin/python

import os
import sys
from osgeo import osr, ogr
from mongoengine import connect
import mongoengine
from documents import VectorFile, Layer
import re

host, port, db, filename, source = sys.argv[1:6]

connect(db, host=host, port=int(port))

parts = filename.split('/')
name = parts[-1]

filename_esc = re.sub('"', "\\\"", re.sub("'", "\\'", filename)) 
name_esc = re.sub('"', "\\\"", re.sub("'", "\\'", name)) 

e4326 = osr.SpatialReference()
e4326.ImportFromEPSG(4326)

_ogr_types = {
    8: "binary",
    9: "date",
    11: "date/time",
    0: "integer",
    1: "integer list",
    2: "real",
    3: "real list",
    4: "string",
    5: "string list",
    10: "time",
    6: "unicode string",
    7: "unicode string list"
}

_ogr_geometries = {
    ogr.wkb25Bit: "25Bit",
    ogr.wkbLineString: "LineString",
    ogr.wkbMultiLineString25D: "MultiLineString25D",
    ogr.wkbMultiPolygon25D: "MultiPolygon25D",
    ogr.wkbPoint25D: "Point25D",
    ogr.wkbXDR: "XDR",
    ogr.wkb25DBit: "25DBit",
    ogr.wkbLineString25D: "LineString25D",
    ogr.wkbMultiPoint: "MultiPoint",
    ogr.wkbNDR: "NDR",
    ogr.wkbPolygon: "Polygon",
    ogr.wkbGeometryCollection: "GeometryCollection",
    ogr.wkbLinearRing: "LinearRing",
    ogr.wkbMultiPoint25D: "MultiPoint25D",
    ogr.wkbNone: "None",
    ogr.wkbPolygon25D: "Polygon25D",
    ogr.wkbGeometryCollection25D: "GeometryCollection25D",
    ogr.wkbMultiLineString: "MultiLineString",
    ogr.wkbMultiPolygon: "MultiPolygon",
    ogr.wkbPoint: "Point",
    ogr.wkbUnknown: "Unknown"
}

if not os.path.exists('/tmp/work'):
    os.mkdir('/tmp/work')

if os.path.exists(filename):
    exit = os.system('mv "{filename}" /tmp/work/"{name}"'.format(name=name_esc, filename=filename_esc))
    if exit != 0:
        sys.stderr.write('?')
        sys.stderr.flush()
        sys.exit(-1)
elif not os.path.exists('/tmp/work/' + name):
    exit = os.system('{icommands}/iget "{filename}" /tmp/work/'.format(
        icommands=os.environ['ICOMMANDS_HOME'],
        filename=filename_esc
    ))
    if exit != 0:
        sys.stderr.write('!')
        sys.stderr.flush()
        sys.exit(-1)

ds = ogr.Open('/tmp/work/{name}'.format(name=name))
if ds:
    v = VectorFile()
    v.filename = name
    v.path = filename
    v.archive = source
    
    v.bbox = [float('inf'), float('inf'), float('-inf'), float('-inf')]
    for l in range(ds.GetLayerCount()):
        lyr = Layer()
        ls = ds.GetLayerByIndex(l)
        lyr.name = ls.GetName()
        lyr.feature_count = ls.GetFeatureCount()
        lyr.record_type = {}
        for col in ls.schema:
            if col.type in _ogr_types:
                lyr.record_type[col.name] = _ogr_types[col.type]
            else:
                lyr.record_type[col.name] = '?'

        extents = ls.GetExtent(force=0)
        if extents:
            w, e, s, n = extents
            srs = ls.GetSpatialRef()
            if srs and srs.ExportToProj4() != e4326.ExportToProj4():
                xform = osr.CoordinateTransformation(srs, e4326)
                w1,s1, _0 = xform.TransformPoint(w,s)
                e1,n1, _0 = xform.TransformPoint(e,n)
                lyr.bbox = [w1,s1,e1,n1]
                if w1 > v.bbox[0]:
                    v.bbox[0] = w1
                if e1 < v.bbox[2]:
                    v.bbox[2] = e1
                if s1 < v.bbox[1]:
                    v.bbox[1] = s1
                if n1 > v.bbox[3]:
                    v.bbox[3] = n1
            else:
                lyr.bbox = [w,s,e,n]
                if w > v.bbox[0]:
                    v.bbox[0] = w
                if e < v.bbox[2]:
                    v.bbox[2] = e
                if s < v.bbox[1]:
                    v.bbox[1] = s
                if n > v.bbox[3]:
                    v.bbox[3] = n
        else:
            lyr.bbox = None

        if lyr.feature_count > 0:
            f = ls.GetNextFeature()
            g = f.GetGeometryRef()
            if g.GetGeometryType() in _ogr_geometries:
                lyr.geography_type = _ogr_geometries[g.GetGeometryType()]
        v.layers.append(lyr)

    if v.bbox[0] == float('inf'):
        v.bbox = None

    try:
        v.save()
        sys.stderr.write('^')
        sys.stderr.flush()
    except mongoengine.queryset.OperationError:
        sys.stderr.write('"')
        sys.stderr.flush()
del ds
os.unlink('/tmp/work/{name}'.format(name=name))
