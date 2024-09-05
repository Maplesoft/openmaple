import openmaple.maplec_ctypes

from openmaple.Expression import ComplexNumeric,Expression,ExpressionSequence,Indexable,List,Name,RealNumeric,RTable,Set,Table

import datetime
import os
import os.path
import pickle
import sys

# Interface implementations
import collections.abc
import decimal
import fractions
import numbers

def _find_maple_binary_dir(search_path, target):
    dirlist=os.listdir(search_path)
    for bdir in dirlist:
        if bdir.startswith('bin'):
            abs_bdir=os.path.join(search_path,bdir)
            for root, _, files in os.walk(abs_bdir):
                if target in files:
                    return root;
    return None

def _find_maple_binary():
    """Return path to Maple binary file."""
    pl=sys.platform
    libpath=None
    # indicate platform-specific binary file
    if pl.startswith('darwin'):
        binfile='libmaplec.dylib'
    elif pl.startswith('linux'):
        binfile='libmaplec.so'
    elif pl.startswith('win32'):
        binfile='maplec.dll'
    # look for binary file under $MAPLE or in directory identified with
    #  platform-specific environment variable
    if 'PYTHONMAPLE' in os.environ:
        libpath=_find_maple_binary_dir(os.environ['PYTHONMAPLE'],binfile)
    elif 'MAPLE' in os.environ:
        libpath=_find_maple_binary_dir(os.environ['MAPLE'],binfile)
    elif pl.startswith('darwin') and 'DYLD_LIBRARY_PATH' in os.environ:
        libpath=os.environ['DYLD_LIBRARY_PATH']
    elif pl.startswith('linux') and 'LD_LIBRARY_PATH' in os.environ:
        libpath=os.environ['LD_LIBRARY_PATH']
    elif pl.startswith('win32') and 'PATH' in os.environ:
        libpath=os.environ['PATH']

    if(libpath is None):
        return None
    paths = libpath.split(os.pathsep)
    for path in paths:
        try:
            dirfiles = os.listdir(path)
        except OSError:
            continue
        if(binfile in dirfiles):
            return(os.path.join(path,binfile))
    return None

class Session:

    def __init__(self):
        """Initialize session."""

        sm_argv = maple.maplec_ctypes.char_pointer()
        self.errorBuf = maple.maplec_ctypes.create_string()
        self.mcbv = maple.maplec_ctypes.buildCallBackVector()

        sofile = _find_maple_binary()
        # if we have not found our object file, die with an error
        if sofile == None:
            raise FileNotFoundError

        # assign our maplec object - sole means of access to Maple C API
        self._maplec = maple.maplec_ctypes.load_maplec(sofile)

        if(self._maplec is None): raise RuntimeError
        self._kv = self._maplec.StartMaple( 0, sm_argv, self.mcbv, 0, 0, self.errorBuf )

    def __del__(self):
        if(self._maplec is None): raise RuntimeError
        kv = self._kv
        maplec = self._maplec
        self._kv = None
        self._maplec = None
        maplec.StopMaple( kv )

    def eval(self, expr, *args):
        if(isinstance(expr,Expression)):
            toeval = self
        else:
            toeval = self._wrap( self._unwrap( expr ) )
        if(isinstance(toeval,Expression)):
            return toeval.eval( *args )
        else:
            return toeval

    def _eval_name(self, nm, symbol=True, wrap=True):
        """Evaluate name to a wrapped Expression."""
        if(symbol == True):
            ret = self._maplec.ToMapleName( self._kv, bytes(nm,'utf-8'), True )
        else:
            ret = self._maplec.EvalMapleStatement( self._kv, bytes(nm+':','utf-8') )
        return (self._wrap(ret) if wrap else ret)

    def _eval_procedure(self, pname, *args, **options):
        return self._wrap( self._eval_procedure_nowrap( pname, *args, **options ) )

    def _eval_procedure_nowrap(self, pname, *args, **options):
        """Call procedure pname and return a wrapped Expression."""
        nargs = len(args)
        if(nargs == 1 and len(options) == 0):
            expseq = self._unwrap( args[0] )
        else:
            expseq = self._maplec.NewMapleExpressionSequence( self._kv, nargs + len(options) )
            # populate positional parameters in function call
            for i in range(0, nargs):
                self._maplec.MapleExpseqAssign( self._kv, expseq, i+1, self._unwrap( args[i] ) )
        j = 0
        # populate optional parameters in function call
        for key in options:
            u = self._maplec.ToMapleName( self._kv, bytes( key, 'utf-8' ), True )
            v = self._unwrap( options[ key ] )
            w = self._maplec.ToMapleRelation( self._kv, b'=', u, v )
            self._maplec.MapleExpseqAssign( self._kv, expseq, nargs+j+1, w )
            j += 1
        if(isinstance(pname,str)):
            fp = self._eval_name( pname, wrap=False )
        else:
            fp = pname
        return self._maplec.EvalMapleProcedure( self._kv, fp, expseq )

    def execute(self, s):
        """Evaluate a string to a wrapped Expression."""
        res = self._maplec.EvalMapleStatement( self._kv, bytes(s, 'utf-8') )
        return self._wrap(res)

    def istype(self, e, typ):
        """Check that e is of the type typ, where typ is an Expression or string."""
        expr = self._unwrap(e)
        if(self._maplec.IsMapleExpressionSequence( self._kv, expr )):
            return False
        elif(isinstance(typ,Expression)):
            u = self._eval_procedure_nowrap( 'type', e, typ )
            return self._maplec.MapleToM_BOOL( self._kv, u )
        elif(typ == 'expseq'):
            return self._maplec.IsMapleExpressionSequence( self._kv, expr )
        elif(typ == 'complex[8]'): 
            return self._maplec.IsMapleComplex64( self._kv, expr )
        elif(typ == 'finite'): 
            return self._maplec.IsMapleComplexNumeric( self._kv, expr )
        elif(typ == 'float' or type == 'float[8]'):  
            return self._maplec.IsMapleFloat64( self._kv, expr )
        elif(typ == 'fraction'): 
            return isinstance(expr, fractions.Fraction)
        elif(typ == 'list' ): 
            return self._maplec.IsMapleList( self._kv, expr )
        elif(typ == 'name'): 
            return self._maplec.IsMapleName( self._kv, expr )
        elif(typ == 'numeric'): 
            return self._maplec.IsMapleNumeric( self._kv, expr )
        elif(typ == 'rational'): 
            return isinstance(expr, int) or isinstance(expr, fractions.Fraction)
        elif(typ == 'rtable'): 
            return self._maplec.IsMapleRTable( self._kv, expr )
        elif(typ == 'set' ): 
            return self._maplec.IsMapleSet( self._kv, expr )
        elif(typ == 'table'): 
            return self._maplec.IsMapleTable( self._kv, expr )
        elif(typ == 'integer'): 
            return isinstance( expr, int )
        elif(typ == 'integer[8]'): 
            return isinstance( expr, int ) and expr.bit_length() < 64
        else:
            u = self._eval_procedure_nowrap( 'type', e, self._eval_name(typ) )
            return self._maplec.MapleToM_BOOL( self._kv, u )

    def range(self, s, t):
        if s != None:
            if t != None:
                return self._eval_procedure('..', s, t)
            else:
                f = self._maplec.EvalMapleStatement( self._kv, b's->s..NULL:' )
                u = self._maplec.EvalMapleProcedure( self._kv, f, self._unwrap(s) )
        elif t != None:
            f = self._maplec.EvalMapleStatement( self._kv, b't->NULL..t:', self._unwrap(t) )
            u = self._maplec.EvalMapleProcedure( self._kv, f, self._unwrap(t) )
        else:
            u = self._maplec.EvalMapleStatement( self._kv, b'NULL..NULL:' )
        return self._wrap( u )

    def symbol(self, s):
        """Return a wrapped Expression with the Maple global name corresponding to string s."""
        res = self._maplec.ToMapleName( self._kv, bytes(s, 'utf-8'), True )
        return self._wrap(res)

    def symbols(self, *args):
        if len(args) == 1:
            if(not isinstance(args[0],str)):
                raise TypeError('symbol must be given as string')
            L=args[0].split(',')
        else:
            for s in args:
                if(not isinstance(s,str)):
                    raise TypeError('symbol must be given as string')
            L=args
        if len(L) == 1:
            s = L[0]
            return self.symbol(s)
        return tuple( [ self.symbol(s) for s in L ] )

    def _wrap(self, expr):
        """Convert a raw Maple ALGEB to a wrapped Expression or Python object."""
        if( self._maplec.IsMapleNumeric( self._kv, expr ) ):
            # Autoconvert exact quantities (integers and fractions)
            if self._maplec.IsMapleInteger64( self._kv, expr ):
                return self._maplec.MapleToInteger64( self._kv, expr )
            elif self._maplec.IsMapleInteger( self._kv, expr ):
                res = self._maplec.MapleALGEB_SPrintf1( self._kv, b'%d', expr )
                return int( self._maplec.MapleToString( self._kv, res ) )
            elif self._maplec.IsMapleFraction( self._kv, expr ):
                u = self._maplec.EvalMapleProcedure( self._kv, self._eval_name('numer',wrap=False), expr )
                v = self._maplec.EvalMapleProcedure( self._kv, self._eval_name('denom',wrap=False), expr )
                return fractions.Fraction( self._wrap(u), self._wrap(v) )
            return RealNumeric( self, expr )
        elif( self._maplec.IsMapleComplexNumeric( self._kv, expr ) ):
            return ComplexNumeric( self, expr )
        elif( self._maplec.IsMapleString( self._kv, expr ) ):
            # Autoconvert strings
            res = self._maplec.MapleToString( self._kv, expr )
            return res.decode('utf-8')
        elif( self._maplec.IsMapleRTable( self._kv, expr ) ):
            return RTable( self, expr )
        elif( self._maplec.IsMapleSet( self._kv, expr )):
            return Set( self, expr )
        elif( self._maplec.IsMapleList( self._kv, expr )):
            return List( self, expr )
        elif( self._maplec.IsMapleExpressionSequence( self._kv, expr ) ):
            return ExpressionSequence( self, expr )
        elif( self._maplec.IsMapleTable( self._kv, expr ) ):
            return Table( self, expr )
        elif( self._maplec.IsMapleName( self._kv, expr ) ):
            res = self._maplec.MapleToString( self._kv, expr )
            # Autoconvert booleans
            if(res == b'true'):
                return True
            elif(res == b'false'):
                return False
            elif(res == b'None'):
                return None
            return Name( self, expr )
        else:
            return Expression( self, expr )
 
    def _unwrap(self, a):
        """Convert a wrapped Expression or Python object to a raw Maple ALGEB."""
        if(isinstance(a,Expression)):
            return a.expr

        # Handle various other types of Python objects
        elif(isinstance(a,bool)):
            return self._maplec.ToMapleBoolean( self._kv, a )
        elif(isinstance(a,int)):
            if(a.bit_length() < 32):
                return self._maplec.ToMapleInteger( self._kv, a )
            return self._eval_procedure_nowrap( 'parse', bytes(str(a),'utf-8') )
        elif(isinstance(a,float)):
            return self._maplec.ToMapleFloat( self._kv, a )
        elif(isinstance(a,str)):
            return self._maplec.ToMapleString( self._kv, bytes(a,'utf-8') )
        elif(isinstance(a,bytes)):
            return self._maplec.ToMapleString( self._kv, a )
        elif(isinstance(a,complex)):
            return self._maplec.ToMapleComplex( self._kv, a.real, a.imag )
        elif(isinstance(a,bytearray)):
            return self._eval_procedure_nowrap( 'convert/ByteArray', bytes(a) )

        elif(isinstance(a,fractions.Fraction)):
            # Use ToMapleFraction if the integers are under 32 bits
            if(a.numerator.bit_length() < 32 and a.denominator.bit_length() < 32):
                return self._maplec.ToMapleFraction( self._kv, a.numerator, a.denominator )
            return self._eval_procedure_nowrap( '/', a.numerator, a.denominator )
        elif(isinstance(a,decimal.Decimal)):
            return self._eval_procedure_nowrap( 'parse', bytes(str(a),'utf-8') )

        elif(isinstance(a,list)):
            u = self._maplec.MapleListAlloc( self._kv, len(a) )
            for i in range(0, len(a)):
                self._maplec.MapleListAssign( self._kv, u, i+1, self._unwrap( a[i] ) )
            return(u)

        elif(isinstance(a,tuple)):
            if(len(a) == 3 and a[1] is Ellipsis):
                return self._eval_procedure_nowrap( '..', a[0], a[2] )
            else:
                u = self._maplec.NewMapleExpressionSequence( self._kv, len(a) )
                for i in range(0, len(a)):
                    self._maplec.MapleExpseqAssign( self._kv, u, i+1, self._unwrap( a[i] ) )
                return u

        elif(isinstance(a,dict)):
            u = self._maplec.MapleTableAlloc( self._kv )
            for key in a:
                v = self._unwrap( key )
                w = self._unwrap( a[key] )
                self._maplec.MapleTableAssign( self._kv, u, v, w )
            return(u)

        elif(isinstance(a,frozenset) or isinstance(a,set)):
            return self._eval_procedure_nowrap( 'convert/set', list(a) )

        elif(a is Ellipsis): 
            return self._maplec.ToMapleName( self._kv, b'..', True )

        elif(a is None): 
            return self._maplec.EvalMapleStatement( self._kv, b'Python:-None:' )

        # Import datetime expressions
        elif(isinstance(a,datetime.date)):
            return self._eval_procedure_nowrap( 'Date', a.year, a.month, a.day )
        elif(isinstance(a,datetime.datetime)):
            return self._eval_procedure_nowrap( 'Date', a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond )
        elif(isinstance(a,datetime.time)):
            raise NotImplementedError
        elif(isinstance(a,datetime.timedelta)):
            p = self._maplec.EvalMapleStatement( self._kv, b"(d,s0,us)->(86400*d+s0+us/1000000)*Units:-Unit('s'):" )
            return self._eval_procedure_nowrap( p, a.days, a.seconds, a.microseconds )

        else: 
            # try importing from other data as a last ditch
            return maple.importfrom.convert( self, a )
