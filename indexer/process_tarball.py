#!/usr/local/bin/python

import sys
import os
import json
import re

host, port, db, filename, ftype = sys.argv[1:6]

parts = filename.split('/')
name = parts[-1]
filename_esc = re.sub('"', "\\\"", re.sub("'", "\\'", filename)) 
name_esc = re.sub('"', "\\\"", re.sub("'", "\\'", name)) 

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

gdal_file = re.compile("(?:" + '|'.join(gdal_formats) + ")$", flags=[re.I])
ogr_file = re.compile("(?:" + '|'.join(ogr_formats) + ")$", flags=[re.I])

formats = set([
    'vrt','tif','ntf','toc','img','gff','asc','ddf','mem',
    'n1','pix','map','mpr','mpl','rgb','hgt','ter','ecw',
    'jp2','grb','rsw','nat','rst','grd','grd','grd','hdr','rda','pnm','hdr',
    'bt','lcp','rik','dem','gxf','grd','grc','gen','blx','sqlite','sdat',

    'shp','e00','bna','dxf','json','gxt','gml','gmt','gpx','gtm','gtz',
    'htf','kml','mif','mid','tab','del','map','id','ind','dgn','sdts',
    'tvp','sua',

    'gz','zip','tar','tgz','bz2','z'
])

limited_formats = set([
    'jpg','png','bmp'
])

world_files = set([
    'wld','jpw','tfw','pnw','pgw','bmw','bpw'
])

if not os.path.exists('/tmp/work'):
    os.mkdir('/tmp/work')

if os.path.exists(filename):
    os.system('mv "{filename}" /tmp/work/"{name}"'.format(filename=filename_esc, name=name_esc))

if not os.path.exists('/tmp/work/' + name):
    print '{icommands}/iget "{filename}" /tmp/work/'.format(
        icommands=os.environ['ICOMMANDS_HOME'],
        filename=filename_esc
    )
    os.system('{icommands}/iget "{filename}" /tmp/work/'.format(
        icommands=os.environ['ICOMMANDS_HOME'],
        filename=filename_esc
    ))

manifest = os.popen('tar -tf /tmp/work/"{name}"'.format(name=name_esc)).read()
if gdal_file.search(manifest) or ogr_file.search(manifest):
    os.system('mkdir -p /tmp/"{name}"; tar -xf /tmp/work/"{name}" -C /tmp/"{name}"/'.format(name=name_esc))
    files = [line.strip() for line in os.popen('find /tmp/"{name}"'.format(name=name_esc)).readlines()][1:]
    extensions = set([x.split('.')[-1].lower() for x in files])
    candidates = filter(lambda x: x.split('.')[-1].lower() in formats or 
                                         (x.split('.')[-1].lower() in limited_formats and len(extensions.intersection(world_files))>0),
                                files)

    if len(candidates) > 0:

        stream = os.popen('./process.py {host} {port} {db} 1 "{filename}"'.format(
            host=host,
            port=port,
            db=db,
            filename=filename_esc), 'w')

        stream.write(json.dumps(files))
        exit = stream.close()
    else:
        sys.stderr.write('0')
        sys.stderr.flush()
else:
    sys.stderr.write('X')

os.system('rm -rf /tmp/"{name}"'.format(name=name_esc))
os.system('rm -rf /tmp/work/"{name}"'.format(name=name_esc))


