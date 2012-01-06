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
    exit = os.system('{icommands}/iget "{filename}" /tmp/work/'.format(
        icommands=os.environ['ICOMMANDS_HOME'],
        filename=filename_esc
    ))
    if exit != 0:
        sys.exit(-1)

os.system('rm -rf /tmp/"{name}"; mkdir -p /tmp/"{name}"; unzip -o -qq -U /tmp/work/"{name}" -d /tmp/"{name}"/'.format(name=name_esc))
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


    stream.write(json.dumps(candidates))
    exit = stream.close()

os.system('rm -rf /tmp/"{name}"'.format(name=name_esc))
os.system('rm /tmp/work/"{name}"'.format(name=name_esc))


