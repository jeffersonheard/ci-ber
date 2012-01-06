from rtree.index import Rtree, CustomStorage, Property
from mongoengine import Document, BinaryField, IntField, StringField, connect
import mongoengine

connect('geotest')

class RTreePage(Document):
    data = BinaryField()
    page = IntField()
    name = StringField()

    @classmethod
    def indices(cls):
        cls.objects.ensure_index("name","page")

class MongoStorage(CustomStorage):
    def __init__(self, name):
        CustomStorage.__init__(self)
        self.db = mongoengine.connection._get_db(reconnect=False)
        self.name = name
        pid = self.db.rtreeseq.find_one({'_id' : self.name})
        if not pid:
            self.db.rtreeseq.insert({'_id' : self.name, "seq" : -1})

    def create(self, returnError):
        """ Called when the storage is created on the C side """

    def destroy(self, returnError):
        """ Called when the storage is destroyed on the C side """

    def clear(self):
        """ Clear all our data """
        RTreePage.objects(name=self.name).delete()
        self.db.rtreeseq.remove({'_id' : self.name})

    def loadByteArray(self, page, returnError):
        """ returns the data for page or returns an error """
        ret = RTreePage.objects(name=self.name, page=page).first()
        if ret:
            return ret.data
        else:
            returnError.contents.value = self.InvalidPageError

    def storeByteArray(self, page, data, returnError):
        """ Stores the data for the page """
        if page == self.NewPage:
            new_pid = self.db.rtreeseq.find_and_modify(query={ "_id" : self.name}, update={"$inc" : {"seq":1}}, new=True, upsert=True)['seq']
            pg = RTreePage(data=data, page=new_pid, name=self.name)
            pg.save(safe=True)
            return new_pid
        else:
            obj = RTreePage.objects(name=self.name, page=page).first()
            if not obj:
                returnError.value = self.InvalidPageError
                return 0
            else:
                obj.data = data
                return page

    def deleteByteArray(self, page, returnError):
        """ Deletes a page """
        try:
            RTreePage.objects(name=self.name, page=page).delete(safe=True)
        except:
            returnError.contents.value = self.InvalidPageError

    hasData = property( lambda self: RTreePage.objects(name=self.name).first() is not None )

if __name__=='__main__':
    settings = Property()
    settings.writethrough= True
    settings.buffering_capacity=1

    storage = MongoStorage('test')
    storage.clear()
    r = Rtree( storage, properties=settings)

    r.add(123,(0,0,1,1))
    
    print "test 1 should be true"
    item = list(r.nearest((0,0), 1, objects=True))[0]
    print item.id
    print r.valid()

    print "test 2 should be true"
    r.delete(123, (0,0,1,1))
    print r.valid()

    print "test 3 should be true"
    r.clearBuffer()
    print r.valid()

    del r

    print "test 4 should be false"
    storage.clear()
    print storage.hasData
    del storage

    print "test 5 should be true"
    storage = MongoStorage('test')
    r1 = Rtree( storage, properties=settings, overwrite=True)
    r1.add(555, (2,2))
    del r1
    print storage.hasData

    print "test 6 should be 1"
    r2 = Rtree( storage, properties = settings, overwrite = False )
    print r2.count( (0,0,10,10) )
    del r2

