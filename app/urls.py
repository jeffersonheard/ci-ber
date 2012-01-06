from django.conf.urls.defaults import *

ciber_prototype12 = patterns('geoanalytics.prototype12.views',
    url(r'^recordgroup', 'recordgroup', name='recordgroup'),
    url(r'^series', 'series', name='series'),
    url(r'^subdirectory', 'subdirectory', name='subdirectory'),
    url(r'^rasterfile', 'rasterfile', name='rasterfile'),
    url(r'^vectorfile', 'vectorfile', name='vectorfile'),
    url(r'^prototype', 'prototype', name='prototype'),
    url(r'^mobile', 'mobile', name='mobile'),
    url(r'^getRGsForBox', 'getRGsForBox', name='getRGsForBox'),
    url(r'^getSeriesForBox', 'getSeriesForBox', name='getSeriesForBox'),
    url(r'^getFilesForBox', 'getFilesForBox', name='getFilesForBox'),
)
