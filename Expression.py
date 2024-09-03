import openmaple

import os
import os.path
import sys

# Python standard library interface implementations
import collections.abc
import datetime
import decimal
import fractions
import numbers
# import numpy for conversions
import numpy

class Expression(collections.abc.Callable,collections.abc.Hashable,collections.abc.Sized):
    """Generic class for all Maple objects."""

    def __init__(self, session, expr):
        self.session = session
        self.expr = expr

    # Unary
    def __abs__(self):
        return self.session._eval_procedure( 'abs', self )

    def __ceil__(self):
        return self.session._eval_procedure( 'ceil', self )

    def __floor__(self):
        return self.session._eval_procedure( 'floor', self )

    def __neg__(self):
        return self.session._eval_procedure( '-', self )

    def __round__(self):
        return self.session._eval_procedure( 'round', self )

    def __trunc__(self):
        return self.session._eval_procedure( 'trunc', self )

    # Binary
    def __add__(self, a):
        return self.session._eval_procedure( '+', self, a )

    def __sub__(self, a):
        return self.session._eval_procedure( '-', self, a )

    def __floordiv__(self, a):
        return self.session._eval_procedure( 'iquo', self, a )

    def __pow__(self, a):
        return self.session._eval_procedure( '^', self, a )

    def __mod__(self, a):
        return self.session._eval_procedure( 'mod', self, a )

    def __mul__(self, a):
        return self.session._eval_procedure( '*', self, a )

    def __truediv__(self, a):
        return self.session._eval_procedure( '/', self, a )

    # Reflected
    def __radd__(self, a): return self.__add__(a)

    def __rfloordiv__(self, a):
        return self.session._eval_procedure( 'iquo', a, self )

    def __rmod__(self, a):
        return self.session._eval_procedure( 'mod', a, self )

    def __rmul__(self, a): return self.__mul__(a)

    def __rpow__(self, a):
        return self.session._eval_procedure( '^', a, self )

    def __rsub__(self, a):
        return self.session._eval_procedure( '-', a, self )

    def __rtruediv__(self, a):
        return self.session._eval_procedure( '/', a, self )

    # Relations
    def __eq__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'=', self.expr, u )
        return self.session._wrap( res )

    def __ge__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'>=', self.expr, u )
        return self.session._wrap( res )

    def __gt__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'>', self.expr, u )
        return self.session._wrap( res )

    def __le__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'<=', self.expr, u )
        return self.session._wrap( res )

    def __lt__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'<', self.expr, u )
        return self.session._wrap( res )

    def __ne__(self, a):
        u = self.session._unwrap( a )
        res = self.session._maplec.ToMapleRelation( self.session._kv, b'<>', self.expr, u )
        return self.session._wrap( res )

    # Callable interface
    def __call__(self, *args, **options):
        return self.session._eval_procedure( self.expr, *args, **options )

    # Conversions to constants
    def __complex__(self):
        u = self.session._eval_procedure( 'evalf', self )
        if isinstance(u, ComplexNumeric):
            return complex(u);
        raise TypeError('complex() argument does not evaluate to a complex numeric')

    def __float__(self):
        u = self.session._eval_procedure( 'evalf', self )
        if isinstance(u, float):
            return u
        raise TypeError('float() argument does not evaluate to a real numeric')

    def __int__(self):
        u = self.session._eval_procedure( 'trunc', self )
        if isinstance(u, int):
            return u
        raise TypeError('int() argument does not evaluate to a real numeric')

    def __str__(self):
        res = self.session._maplec.MapleALGEB_SPrintf1( self.session._kv, b'%q', self.expr )
        s = self.session._maplec.MapleToString( self.session._kv, res )
        return s.decode('utf-8')

    # getitem implementation
    def __getitem__(self, a):
        return self.session._eval_procedure( '?[]', self, [a] )

    # Hashable interface
    def __hash__(self):
        return int( self.expr )

    # Sized interface
    def __len__(self):
        return self.session._eval_procedure( 'length', self )

    # Printing
    def __repr__(self):
        res = self.session._maplec.MapleALGEB_SPrintf1( self.session._kv, b'%q', self.expr )
        s = self.session._maplec.MapleToString( self.session._kv, res )
        return s.decode('utf-8')

    def _repr_latex_(self):
        res = self.session._eval_procedure_nowrap( 'latex', self, output = self.session._eval_name('string') )
        s = self.session._maplec.MapleToString( self.session._kv, res )
        return ('$$' + s.decode('utf-8') + '$$')

    # Maple-specific methods
    def eval(self, *args):
        return self.session._eval_procedure( 'eval', self, *args )

    def unique(self):
        res = self.session._maplec.MapleUnique( self.session._kv, self.expr )
        if(res == self.expr):
            return self
        return self.session._wrap(res)

    def uneval(self):
        res = self.session._maplec.ToMapleUneval( self.session._kv, self.expr )
        return self.session._wrap(res)

class ComplexNumeric(Expression,numbers.Complex):
    """Maple complex numeric objects."""

    def __complex__(self):
        rp = self.session._maplec.MapleSelectRealPart( self.session._kv, self.expr )
        rp = self.session._maplec.MapleEvalhf( self.session._kv, rp )
        ip = self.session._maplec.MapleSelectImaginaryPart( self.session._kv, self.expr )
        ip = self.session._maplec.MapleEvalhf( self.session._kv, ip )
        return (rp + 1j*ip)

    def __init__(self, session, expr):
        Expression.__init__(self, session, expr)

    def __pos__(self):
        return self

    # Complex operations
    def conjugate(self):
        return self.session._eval_procedure( 'conjugate', self )

    def imag(self):
        res = self.session._maplec.MapleSelectImaginaryPart( self.session._kv, self.expr )
        return self.session._wrap( res )

    def real(self):
        res = self.session._maplec.MapleSelectRealPart( self.session._kv, self.expr )
        return self.session._wrap( res )

    def to_python(self):
        raise "cannot convert to Python"

class RealNumeric(ComplexNumeric,numbers.Real):
    """Maple real numeric objects."""

    def __init__(self, session, expr):
        ComplexNumeric.__init__(self, session, expr)

    def __divmod__(self, a):
        q = self.session._eval_procedure( 'iquo', self, a )
        r = self.session._eval_procedure( 'irem', self, a )
        return (q, r)

    def __float__(self):
        return self.session._maplec.MapleEvalhf( self.session._kv, self.expr )

    def __int__(self):
        return trunc( self )

    def as_integer_ratio(self):
        u = self.session._eval_procedure( 'convert/fraction', self )
        return (u.numerator, u.denominator)

    def imag(self):
        return 0

    def real(self):
        return self

    def to_python(self):
        return float(self)

class Name(Expression):
    """Maple symbols and names."""

    def __init__(self, session, expr):
        Expression.__init__(self, session, expr)

    # Implements a.b as a:-b
    def __getattr__(self, attr):
        exportName = self.session.symbol( attr )
        return self.session._eval_procedure( 'index', self, exportName )

    def assign(self, expr):
        u = self.session._unwrap( expr )
        res = self.session._maplec.MapleAssign( self.session._kv, self.expr, u )
        return self.session._wrap(res)

class Indexable(Expression,collections.abc.Collection):
    """Superclass for Maple indexable objects."""

    def __init__(self, session, expr):
        Expression.__init__(self, session, expr)

    def __contains__(self, expr):
        res = self.session._eval_procedure_nowrap( 'member', expr, self )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        return self.session._maplec.MapleNumElements( self.session._kv, self.expr )

class ExpressionSequence(Indexable,collections.abc.Sequence):
    """Maple expression sequences."""

    def __init__(self, session, expr):
        Indexable.__init__(self, session, expr)

    def __contains__(self, expr):
        aslist = self.session._eval_procedure( '[]', self )
        res = self.session._eval_procedure_nowrap( 'member', expr, aslist )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    # getitem implementation
    def __getitem__(self, a):
        aslist = self.session._eval_procedure( '[]', self )
        return self.session._eval_procedure( '?[]', aslist, [a] )

    def __iter__(self):
        aslist = self.session._eval_procedure( '[]', self )
        return IndexableIterator( aslist )

    def __len__(self):
        return self.session._maplec.MapleNumArgs( self.session._kv, self.expr )

    def __reversed__(self):
        aslist = self.session._eval_procedure( '[]', self )
        return ReverseListIterator( aslist )

    def index(self, expr):
        mindex = self.session._maplec.EvalMapleStatement( self.session._kv, b'proc(a,b) local pos; ifelse(member(a,[b],pos),pos,0) end:' )
        res = self.session._eval_procedure( mindex, expr, self )
        if(res == 0):
            raise ValueError('is not in expression sequence')
        return res

class List(Indexable,collections.abc.Sequence):
    """Maple lists."""

    def __init__(self, session, expr):
        Indexable.__init__(self, session, expr)

    def __iter__(self):
        return IndexableIterator( self )

    def __reversed__(self):
        return ReverseListIterator( self )

    def index(self, expr):
        mindex = self.session._maplec.EvalMapleStatement( self.session._kv, b'proc(a,b) local pos; ifelse(member(a,b,pos),pos,0) end:' )
        res = self.session._eval_procedure( mindex, expr, self )
        if(res == 0):
            raise ValueError('is not in list')
        return res

class Set(Indexable,collections.abc.Set):
    """Maple sets."""

    def __init__(self, session, expr):
        Indexable.__init__(self, session, expr)

    def __iter__(self):
        aslist = self.session._eval_procedure( 'convert/list', self )
        return iter(aslist)

    # Relations
    def __le__(self, a):
        res = self.session._eval_procedure_nowrap( 'subset', self, a )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    def __lt__(self, a):
        if self.session._maplec.ToMapleRelation( self.session._kv, b'=', self.expr, a.expr ):
            return False
        res = self.session._eval_procedure_nowrap( 'subset', self, a )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    def __ge__(self, a):
        res = self.session._eval_procedure_nowrap( 'subset', a, self )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    def __gt__(self, a):
        if self.session._maplec.ToMapleRelation( self.session._kv, b'=', self.expr, a.expr ):
            return False
        res = self.session._eval_procedure_nowrap( 'subset', a, self )
        return self.session._maplec.MapleToM_BOOL( self.session._kv, res )

    def __and__(self, a):
        return self.session._eval_procedure( 'intersect', self, a )

    def __or__(self, a):
        return self.session._eval_procedure( 'union', self, a )

    def __xor__(self, a):
        return self.session._eval_procedure( 'symmdiff', self, a )

    def __sub__(self, a):
        return self.session._eval_procedure( 'minus', self, a )

    def isdisjoint(self, a):
        res = self.session._eval_procedure_nowrap( 'intersect', self, a )
        size = self.session._maplec.MapleNumElements( self.session._kv, res )
        return (size == 0)

class RTable(Indexable):
    """Maple rectangular tables (including Matrix and Vector objects)."""

    def __bytes__(self):
        res = self.session._eval_procedure_nowrap( 'type/ByteArray', self )
        if self.session._maplec.MapleToM_BOOL( self.session._kv, res ):
            return bytes( list( self ) )
        raise TypeError("cannot convert to bytes")

    def __init__(self, session, expr):
        Indexable.__init__(self, session, expr)

    def __iter__(self):
        res = self.session._eval_procedure_nowrap( 'convert/list', self )
        return IndexableIterator( self.session._wrap( res ) )  

    def to_list_nested(self, a):
        if( self.session._maplec.IsMapleList( self.session._kv, a.expr )):
            return( [ x for x in a ] )
        else:
            return a

    def to_numpy(self):
        res = self.session._eval_procedure( 'convert', self,
            self.session.symbol('list'), self.session.symbol('nested')
        )
        return numpy.array( self.to_list_nested( res ) )

    def to_python(self):
        if(numpy is None):
            return RuntimeError   
        return to_numpy(self)

class Table(Indexable,collections.abc.MutableMapping):
    """Maple tables (key/value pairs)."""

    def __init__(self, session, expr):
        Indexable.__init__(self, session, expr)

    def __iter__(self):
        return TableIterator( self )  

    def __contains__(self, key):
        u = self.session._unwrap( key )
        return self.session._maplec.MapleTableHasEntry( self.session._kv, self.expr, u )

    def __delitem__(self, key):
        u = self.session._unwrap( key )
        res = self.session._maplec.MapleTableDelete( self.session._kv, self.expr, u )
        return None

    def __getitem__(self, key):
        u = self.session._unwrap( key )
        res = self.session._maplec.MapleTableSelect( self.session._kv, self.expr, u )
        return self.session._wrap( res )

    def __setitem__(self, key, expr):
        u = self.session._unwrap( key )
        v = self.session._unwrap( expr )
        res = self.session._maplec.MapleTableAssign( self.session._kv, self.expr, u, v )
        return None

    def keys(self):
        fp = self.session._maplec.ToMapleName( self.session._kv, b'lhs', True )
        res = self.session._eval_procedure_nowrap( 'convert/equationlist', self )
        n = self.session._maplec.MapleNumElements( self.session._kv, res )
        return [ self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, fp, self.session._maplec.MapleListSelect( self.session._kv, res, i+1 ) ) ) for i in range(0,n) ]

    def items(self):
        lhs = self.session._maplec.ToMapleName( self.session._kv, b'lhs', True )
        rhs = self.session._maplec.ToMapleName( self.session._kv, b'rhs', True )
        res = self.session._eval_procedure_nowrap( 'convert/equationlist', self )
        n = self.session._maplec.MapleNumElements( self.session._kv, res )
        L = [ self.session._maplec.MapleListSelect( self.session._kv, res, i+1 ) for i in range(0,n) ]
        return [ 
          ( self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, lhs, x ) ), 
            self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, rhs, x ) ) )
            for x in L ]

    def to_python(self):
        lhs = self.session._maplec.ToMapleName( self.session._kv, b'lhs', True )
        rhs = self.session._maplec.ToMapleName( self.session._kv, b'rhs', True )
        res = self.session._eval_procedure_nowrap( 'convert/equationlist', self )
        n = self.session._maplec.MapleNumElements( self.session._kv, res )
        L = [ self.session._maplec.MapleListSelect( self.session._kv, res, i+1 ) for i in range(0,n) ]
        pyhash = {}
        for x in L:
            u = self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, lhs, x ) )
            pyhash[u] = self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, rhs, x ) )
        return pyhash

    def values(self):
        fp = self.session._maplec.ToMapleName( self.session._kv, b'rhs', True )
        res = self.session._eval_procedure_nowrap( 'convert/equationlist', self )
        n = self.session._maplec.MapleNumElements( self.session._kv, res )
        return [ self.session._wrap( self.session._maplec.EvalMapleProcedure( self.session._kv, fp, self.session._maplec.MapleListSelect( self.session._kv, res, i+1 ) ) ) for i in range(0,n) ]

class IndexableIterator:
    """Iterator over generic Indexable objects)."""

    def __init__(self, a):
        self.expr = a.expr
        self.idx = 0
        self.session = a.session

    def __iter__(self, /):
        return self

    def __next__(self, /):
        self.idx += 1
        n = self.session._maplec.MapleNumElements( self.session._kv, self.expr )
        if(self.idx > n):
            self.idx = 0
            raise StopIteration  # Done iterating.
        res = self.session._maplec.MapleListSelect( self.session._kv, self.expr, self.idx )
        return self.session._wrap( res )

class ReverseListIterator:
    """Iterator over List in reverse direction)."""

    def __init__(self, a):
        self.expr = a.expr
        self.idx = 0
        self.session = a.session

    def __iter__(self, /):
        return self

    def __next__(self, /):
        self.idx += 1
        n = self.session._maplec.MapleNumElements( self.session._kv, self.expr )
        if(self.idx > n):
            self.idx = 0
            raise StopIteration  # Done iterating.
        res = self.session._maplec.MapleListSelect( self.session._kv, self.expr, n-self.idx+1 )
        return self.session._wrap( res )

class TableIterator(IndexableIterator):
    """Iterator over Table objects)."""

    def __init__(self, a):
        res = a.session._eval_procedure_nowrap( 'convert/equationlist', a )
        self.idx = 0
        self.expr = res
        self.session = a.session

    def __iter__(self, /):
        return self

    def __next__(self):
        self.idx += 1
        n = self.session._maplec.MapleNumElements( self.session._kv, self.expr )
        if(self.idx > n):
            self.idx = 0
            raise StopIteration  # Done iterating.
        return self.session._eval_procedure( 'lhs', self, self.idx )
