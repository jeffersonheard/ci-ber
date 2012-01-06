#!/usr/local/bin/python

from multiprocessing import Pool
import os
import sys
import json
from mongoengine import connect
from documents import RegularFile

host, port, db, procs = sys.argv[1:5]
procs = int(procs)
source = ""
local = False
if len(sys.argv) == 6:
    local = True
    source = sys.argv[5]

connect(db, host=host, port=int(port))

gdal_formats = set([
    'vrt','tif','ntf','toc','img','gff','asc','ddf','mem',
    'n1','pix','map','mpr','mpl','rgb','hgt','ter','ecw',
    'jp2','grb','rsw','nat','rst','grd','grd','grd','hdr','rda','pnm','hdr',
    'bt','lcp','rik','dem','gxf','grd','grc','gen','blx','sqlite','sdat', 'hdf',
    'jpg','gif','png','bmp'])

ogr_formats = set([
    'shp','e00','bna','dxf','json','gxt','gml','gmt','gpx','gtm','gtz',
    'htf','kml','mif','mid','tab','del','map','id','ind','dgn','sdts',
    'tvp','sua'])

compression_programs = {
    'gz' : 'gunzip',
    'tgz' : 'gunzip',
    'bz2' : 'bunzip2',
    'z' : 'uncompress'
}


def f(filename):
    try:
        parts = [t.lower() for t in filename.split('.')]
        ftype = zipball = tarball = gzip = is_ogr = is_gdal = False

        extn = parts[-1]
        program = None
        source = "" 

        if extn in compression_programs:
            program = compression_programs[parts[-1]]
            extn = parts[-2]
            if extn == 'tgz':
                tarball = True

        if extn in ogr_formats:
            ftype = 'ogr'
        elif extn in gdal_formats:
            ftype = 'gdal'
        elif extn == 'zip':
            zipball = True
        elif extn == 'tar':
            tarball = True

        if program and (ftype or tarball):
            print (ftype, tarball, filename)
            filename,source = os.popen('./process_compression.py {filename} {program}'.format(filename=filename, program=program)).readlines()
            filename.strip()
            source.strip()
            if not filename:
                return

        if tarball:
            os.system('./process_tarball.py {host} {port} {db} "{filename}" "{source}"'.format(
                    host=host, port=port, db=db, filename=filename, source=source))
            sys.stderr.write('tarball')
        elif zipball:
            os.system('./process_zipball.py {host} {port} {db} "{filename}" "{source}"'.format(
                    host=host, port=port, db=db, filename=filename, source=source))
        elif ftype == 'ogr':
            sys.stderr.write('ogr\n')
            os.system('./index_vector.py {host} {port} {db} "{filename}" "{source}"'.format(
                    host=host, port=port, db=db, filename=filename, source=source))
        elif ftype == 'gdal':
            sys.stderr.write('gdal\n')
            os.system('./index_raster.py {host} {port} {db} "{filename}" "{source}"'.format(
                    host=host, port=port, db=db, filename=filename, source=source))
        else:
            sys.stderr.write(extn)
    except Exception as e:
        print e

p = Pool(procs)
i = 0
for data in sys.stdin:
    i += 1
    data = json.loads(data)
    if i % 100 == 0:
        sys.stderr.write('.')
        sys.stderr.flush()
    if i % 5000 == 0:
        sys.stderr.write(' ')
        sys.stderr.flush()
    p.map(f, data)
