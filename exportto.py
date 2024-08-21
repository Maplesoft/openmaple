from importlib import import_module
from importlib.util import find_spec
from openmaple.Expression import Expression

import datetime
import decimal
import fractions
import numbers

pandas = find_spec('pandas') and import_module('pandas') or None
PIL = find_spec('PIL') and import_module('PIL') or None
if PIL is not None: PIL.Image = import_module('PIL.Image')
numpy = find_spec('numpy') and import_module('numpy') or None
scipy = find_spec('scipy') and import_module('scipy') or None
sympy = find_spec('sympy') and import_module('sympy') or None
tensorflow = None

class exportto:

    def evaluate(sess, expr):
        if(not isinstance( expr, Expression )):
            return expr

        a = sess._unwrap( expr )

        if sess.istype( expr, 'numeric' ):

            if sess.istype( expr, 'integer' ):
                if sess._maplec.IsMapleInteger64( sess._kv, a ):
                    return sess._maplec.MapleToInteger64( sess._kv, a )
                else:
                    return fractions.Fraction( str( expr ) )

            elif sess.istype( expr, 'fraction' ):
                b = str( sess._eval_procedure( 'numer', expr ) )
                c = str( sess._eval_procedure( 'denom', expr ) )
                return fractions.Fraction( b ) / fractions.Fraction( c )

            elif sess._maplec.IsMapleFloat64( sess._kv, a ):
                return sess._maplec.MapleToFloat64( sess._kv, a )

            else: # software float that will not fit in hardware without truncation
                b = str( sess._eval_procedure( 'SFloatMantissa', expr ) )
                c = str( sess._eval_procedure( 'SFloatExponent', expr ) )
                return decimal.Decimal(b) * 10 ** decimal.Decimal(c)

        elif sess._maplec.IsMapleComplexNumeric( sess._kv, a ):
            b = sess._eval_procedure_nowrap( 'Re', expr )
            c = sess._eval_procedure_nowrap( 'Im', expr )

            if sess._maplec.IsMapleFloat64( sess._kv, b ) and sess._maplec.IsMapleFloat64( sess._kv, c ):
                return complex( sess._maplec.MapleToFloat64( sess._kv, b ), sess._maplec.MapleToFloat64( sess._kv, c ) )

            else:
                return complex( self._wrap(b), self._wrap(c) )
            
        elif sess.istype( expr, 'rtable' ):
            raise NotImplementedError

        elif sess.istype( expr, 'table' ):
            raise NotImplementedError

 #       elif sess.istype( expr, 'Date' ):
 #           raise NotImplementedError

        else: 
            raise RuntimeError
