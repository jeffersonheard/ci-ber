#!/usr/local/bin/python

import os
import sys
from osgeo import gdal, osr
from documents import RasterFile, Band, DamagedRasterFile
from mongoengine import connect
import mongoengine
import re
 
host, port, db, filename, source = sys.argv[1:6]

connect(db, host=host, port=int(port))

parts = filename.split('/')
name = parts[-1]

filename_esc = re.sub('"', "\\\"", re.sub("'", "\\'", filename)) 
name_esc = re.sub('"', "\\\"", re.sub("'", "\\'", name)) 

_gdal_types = {
    gdal.GDT_Byte: "Byte",
    gdal.GDT_CFloat64: "CFloat64",
    gdal.GDT_CInt32: "CInt32",
    gdal.GDT_Float64: "Float64",
    gdal.GDT_Int32: "Int32",
    gdal.GDT_UInt16: "UInt16",
    gdal.GDT_Unknown: "Unknown",
    gdal.GDT_CFloat32: "CFloat32",
    gdal.GDT_CInt16: "CInt16",
    gdal.GDT_Float32: "Float32",
    gdal.GDT_Int16: "Int16",
    gdal.GDT_TypeCount: "TypeCount",
    gdal.GDT_UInt32: "UInt32"
}

_gdal_interps = {
    gdal.GCI_AlphaBand: "AlphaBand",
    gdal.GCI_CyanBand: "CyanBand",
    gdal.GCI_HueBand: "HueBand",
    gdal.GCI_PaletteIndex: "PaletteIndex",
    gdal.GCI_Undefined: "Undefined",
    gdal.GCI_YCbCr_YBand: "YCbCr_YBand",
    gdal.GCI_BlackBand: "BlackBand",
    gdal.GCI_GrayIndex: "GrayIndex",
    gdal.GCI_LightnessBand: "LightnessBand",
    gdal.GCI_RedBand: "RedBand",
    gdal.GCI_YCbCr_CbBand: "YCbCr_CbBand",
    gdal.GCI_YellowBand: "YellowBand",
    gdal.GCI_BlueBand: "BlueBand",
    gdal.GCI_GreenBand: "GreenBand",
    gdal.GCI_MagentaBand: "MagentaBand",
    gdal.GCI_SaturationBand: "SaturationBand",
    gdal.GCI_YCbCr_CrBand: "YCbCr_CrBand"
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

ds = gdal.Open('/tmp/work/{name}'.format(name=name_esc))
if ds:
    r = RasterFile()
    r.description = ds.GetDescription()
    r.srs = ds.GetProjectionRef()
    r.metadata = ds.GetMetadata()
    r.path = filename
    r.filename = name
    r.archive = source
    r.bands = []
    
    x1, dx, _1, y1, _2, dy = ds.GetGeoTransform()

    if r.srs:
        if r.srs != "EPSG:4326":
            s_srs = osr.SpatialReference()
            s_srs.ImportFromWkt(ds.GetProjectionRef())
            t_srs = osr.SpatialReference()
            t_srs.ImportFromEPSG(4326)
            xs = ds.RasterXSize
            ys = ds.RasterYSize
            xform = osr.CoordinateTransformation(s_srs, t_srs)
            llx, lly, _1 = xform.TransformPoint(x1, y1, 0)
            urx, ury, _1 = xform.TransformPoint(x1+dx*xs, y1+dy*ys)
            r.bbox = [llx,lly,urx,ury]
            #if r.srs or (x1 > 0.01 and y1 > 0.01 and dx != 1 and dy != 1):
        x1, dx, _1, y1, _2, dy = ds.GetGeoTransform()
        xs = ds.RasterXSize
        ys = ds.RasterYSize
        r.bbox = [x1, y1+ys*dy, x1+xs*dx, y1]

        for b in range(1, ds.RasterCount+1):
            bs = ds.GetRasterBand(b)
            band = Band()
            band.datatype = _gdal_types[bs.DataType]
            band.rows = bs.XSize
            band.cols = bs.YSize
            band.metadata = dict(bs.GetMetadata())
            band.min_val = bs.GetMinimum()
            band.max_val = bs.GetMaximum()
            band.offset = bs.GetOffset()
            band.description = str(bs.GetDescription())
            band.color_interp = _gdal_interps[bs.GetColorInterpretation()]

            band.validate()

            r.bands.append(band)
        try:
            r.save()
            sys.stderr.write('#')
            sys.stderr.flush()
        except mongoengine.queryset.OperationError:
            sys.stderr.write('"')
            sys.stderr.flush()
    else:
        d = DamagedRasterFile()
        d.description = r.description
        d.srs = r.srs
        d.path = r.path
        d.filename = r.filename
        d.archive = r.archive
        d.bands = r.bands
        d.metadata = r.metadata
        for b in range(1, ds.RasterCount+1):
            bs = ds.GetRasterBand(b)
            band = Band()
            band.datatype = _gdal_types[bs.DataType]
            band.rows = bs.XSize
            band.cols = bs.YSize
            band.metadata = dict(bs.GetMetadata())
            band.min_val = bs.GetMinimum()
            band.max_val = bs.GetMaximum()
            band.offset = bs.GetOffset()
            band.description = str(bs.GetDescription())
            band.color_interp = _gdal_interps[bs.GetColorInterpretation()]

            band.validate()

            d.bands.append(band)
        d.save()

del ds
os.unlink('/tmp/work/{name}'.format(name=name))
