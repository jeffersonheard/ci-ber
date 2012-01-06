# Create your views here.

from geoanalytics.userdata.navbar import Navbar
from document import RecordGroup, Series, Subdirectory, RasterFile, VectorFile
from pymongo import json_util
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from rtree import Rtree
import json

def _make_node(item):
    data = item.to_mongo()
    name = None
    try:
        name=item.name
    except:
        name=item.filepath

    if 'total_files' in data:
        data['$area'] = data['total_files']
    else:
        data['$area'] = 1

    return { 'children' : [], 'data' : data, 'name' : name, 'id' : str(item.id) }

def _fudge(items):
    for k,v in items:
        try:
            yield (k, int(v))
        except ValueError:
            try:
                yield(k, float(v))
            except ValueError:
                yield (k,v)

def recordgroup(request):
    o = { 'children' : [_make_node(d) for d in RecordGroup.objects(**dict(_fudge(request.REQUEST.items())))] }
    return HttpResponse(json.dumps(o,  default=json_util.default), mimetype='application/json')
    
def series(request):
    o = { 'children' : [_make_node(d) for d in Series.objects(**dict(_fudge(request.REQUEST.items())))] }
    return HttpResponse(json.dumps(o,  default=json_util.default), mimetype='application/json')
    
def subdirectory(request):
    o = { 'children' : [_make_node(d) for d in Subdirectory.objects(**dict(_fudge(request.REQUEST.items())))] }
    return HttpResponse(json.dumps(o,  default=json_util.default), mimetype='application/json')
    
def rasterfile(request):
    o = { 'children' : [_make_node(d) for d in RasterFile.objects(**dict(_fudge(request.REQUEST.items())))] }
    return HttpResponse(json.dumps(o,  default=json_util.default), mimetype='application/json')
    
def vectorfile(request):
    o = { 'children' : [_make_node(d) for d in VectorFile.objects(**dict(_fudge(request.REQUEST.items())))] }
    return HttpResponse(json.dumps(o,  default=json_util.default), mimetype='application/json')
    
def prototype(request):
    return render_to_response('ciber/prototype12.html', {'navbar' : Navbar(request.user)}, context_instance=RequestContext(request));

def mobile(request):
    for key, value in request.REQUEST.items():
        print (key, value)
    return render_to_response('ciber/bbox-lookkup.html', {}, context_instance=RequestContext(request));


def getRGsForBox(request):
    l = float( request.GET['x1'] )
    b = float( request.GET['y1'] )
    r = float( request.GET['x2'] )
    t = float( request.GET['y2'] )
    
    index = Rtree('/home/renci/geoanalytics/geoanalytics-lib/rg')
    ids = list(index.intersection((l,b,r,t), objects=True))
    rgs = []
    if len(ids) > 0:
        rgs = [{
            'name' : r.name,
            'filepath' : r.filepath, 
            'bounds' : r.bbox4326, 
            'seriescount' : Series.objects(record_group=r).count() 
        } for r in [RecordGroup.objects(id=i.object).first() for i in ids]]
    return HttpResponse(json.dumps(rgs), mimetype='application/json')

def getSeriesForBox(request):
    l = float( request.GET['x1'] )
    b = float( request.GET['y1'] )
    r = float( request.GET['x2'] )
    t = float( request.GET['y2'] )
    rg = request.GET['rg']

    index = Rtree('/home/renci/geoanalytics/geoanalytics-lib/sr')
    ids = list(index.intersection((l,b,r,t), objects=True))
    if len(ids)> 0:
        sers = [{
            'name' : s.name,
            'filepath' : s.filepath,
            'bounds' : s.bbox4326,
            'filecount' : VectorFile.objects(series=s).count() + RasterFile.objects(series=s).count()
        } for s in [Series.objects(id=i.object[0]).first() for i in filter(lambda x:x.object[1] == rg, ids)]]
        return HttpResponse(json.dumps(sers), mimetype='application/json')
    else:
        return HttpResponse("[]", mimetype='application/json')

def getFilesForBox(request):
    l = float( request.GET['x1'] )
    b = float( request.GET['y1'] )
    r = float( request.GET['x2'] )
    t = float( request.GET['y2'] )
    ser = request.GET['ser']
    begin = int(request.GET['begin'])
    num = int(request.GET['num'])

    index = Rtree('/home/renci/geoanalytics/geoanalytics-lib/fl')
    ids = list(index.intersection((l,b,r,t), objects=True))[begin:begin+num]
    if len(ids)>0:
        files = [{
            'name' : f.name,
            'filepath' : f.filepath,
            'bbox4326' : f.bbox4326,
            'metadata' : f.metadata,
            'type' : "raster",
            'band_metadata' : f.band_metadata,
            'projection' : f.projection
        } for f in [RasterFile.objects(id=i.object[0]).first() for i in filter(lambda x:x.object[1]==ser and x.object[2] == 'r' , ids)]] + [{
            'name' : f.name,
            'filepath' : f.filepath,
            'bbox4326' : f.bbox4326,
            'type' : "features",
            'attributes' : f.attribute_names,
            'layers' : [{'attributes' : zip(l.attribute_names, l.attribute_types), 
                         'geometry_type' : l.geometry_type, 
                         'feature_count' : l.feature_count} for l in f.layers]
        } for f in [VectorFile.objects(id=i.object[0]).first() for i in filter(lambda x:x.object[1]==ser and x.object[2] == 'v' , ids)]] 
        return HttpResponse(json.dumps(files), mimetype='application/json')
    else:
        return HttpResponse("[]", mimetype='application/json')

