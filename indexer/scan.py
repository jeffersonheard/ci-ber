#!/usr/local/bin/python2.7

import os
import sys
import json
from pprint import PrettyPrinter
from documents import Directory
from mongoengine import connect

host, port, db = sys.argv[1:4]

formats = set([
    'vrt','tif','ntf','toc','img','gff','asc','ddf','mem',
    'n1','pix','map','mpr','mpl','rgb','hgt','ter','ecw',
    'jp2','grb','rsw','nat','rst','grd','grd','grd','hdr','rda','pnm','hdr',
    'bt','lcp','rik','dem','gxf','grd','grc','gen','blx','sqlite','sdat',

    'shp','dbf','shx','e00','bna','dxf','json','gxt','gml','gmt','gpx','gtm','gtz',
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

connect(db, host=host, port=int(port))

pp = PrettyPrinter(indent=4)
stack = []
restart = None
printing = True

if len(sys.argv) > 5:
    restart = sys.argv[5]
    printing = False

# ------------------------------------------------------------------------------
def qPOSIX(string):
        output = "'"
        output += string.replace( "'", r"\'" )
        output += "'"

        return output

def scan(directory):
    global stack
    try:
        entries = os.popen(os.environ['ICOMMANDS_HOME'] + '/ils "' + directory + '"').read().split('\n')[1:-1]
        files = filter(lambda x: not x.startswith('  C- '), entries)
        extensions = set([x.split('.')[-1].lower() for x in files])
        candidates = filter(lambda x: x.split('.')[-1].lower() in formats or 
                                     (x.split('.')[-1].lower() in limited_formats and len(extensions.intersection(world_files))>0),
                            files)
        directories = filter(lambda x: x.startswith('  C- '), entries)

        dr = Directory(
            name = directory,
            files = files,
            subdirectories = directories,
            candidates = candidates
        )
        dr.save()
    except Exception as e:
        sys.stderr.write(str(e))
        sys.stderr.flush()

    stack.extend(list([d[5:] for d in directories]))
    if len(candidates) > 0:
        return list([(directory + '/' + f.strip()) for f in files])
    else:
        return None


# ------------------------------------------------------------------------------

groups = json.loads(sys.stdin.read())

stack = groups
while len(stack) > 0:
    files = scan(stack.pop())
    if files:
        sys.stderr.write(str(len(files)) + '`')
        sys.stderr.flush()
        if printing:
            print(json.dumps(files))
        else:
            try:
                k = files.index(restart)
                files = files[k+1:]
                printing = True
                if len(files):
                    print(json.dumps(files))
            except Exception as e:
                sys.stderr.write(str(e))
                sys.stderr.flush()

sys.stderr.write("Done!")
sys.stderr.flush()
sys.stdout.close()
