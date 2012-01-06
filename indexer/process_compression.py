#!/usr/local/bin/python

import sys
import os
import re

filename, program = sys.argv[1:3]

parts = filename.split('/')
name = parts[-1]
filename_esc = re.sub('"', "\\\"", re.sub("'", "\\'", filename)) 
name_esc = re.sub('"', "\\\"", re.sub("'", "\\'", name)) 

if not os.path.exists('/tmp/work/' + name):
    os.system('{icommands}/iget "{filename}" /tmp/work/'.format(
        icommands=os.environ['ICOMMANDS_HOME'],
        filename=filename_esc
    ))

os.system('{program} /tmp/work/"{name}"'.format(program=program, name=name_esc))
    
print '.'.join(filename.split('.')[0:-1])
print filename
