import sys
import maple

class LibraryInstance:

    def __getattr__(self, attr):
        if(attr == '__spec__'):
            return None
        sess = maple.getactive()
        if(sess):
            sym = sess._wrap( sess._maplec.ToMapleName( sess._kv, bytes( attr, 'utf-8' ), True ) )
        else:
            sym = None
        return sym

    def __setattr__(self, attr, value):
        if(attr == '__spec__'):
            return None
        sess = maple.getactive()
        if(sess):
            sym = sess._maplec.ToMapleName( sess._kv, bytes( attr, 'utf-8' ), True )
            sess._maplec.MapleAssign( sess._kv, sym, sess._unwrap( value ) )
        return None

sys.modules[__name__] = LibraryInstance()
