from importlib import import_module
from importlib.util import find_spec

# supported packages
pandas = find_spec('pandas') and import_module('pandas') or None
PIL = find_spec('PIL') and import_module('PIL') or None
if PIL is not None: PIL.Image = import_module('PIL.Image')
numpy = find_spec('numpy') and import_module('numpy') or None
scipy = find_spec('scipy') and import_module('scipy') or None
mpmath = find_spec('mpmath') and import_module('mpmath') or None
sympy = find_spec('sympy') and import_module('sympy') or None

class importfrom:

    def convert(sess, a):

        # Import numpy expressions
        if(numpy is not None and isinstance(a,numpy.ndarray)):
            # FIXME: use lists as intermediate representation
            shp = numpy.shape(a)
            dtyp = a.dtype
            if(dtyp == numpy.dtype('int64')):
                typ=sess._eval_name( 'integer[8]', symbol=False )
            elif(dtyp == numpy.dtype('int32')):
                typ=sess._eval_name( 'integer[4]', symbol=False )
            elif(dtyp == numpy.dtype('int16')):
                typ=sess._eval_name( 'integer[2]', symbol=False )
            elif(dtyp == numpy.dtype('int8')):
                typ=sess._eval_name( 'integer[1]', symbol=False )
            elif(dtyp == numpy.dtype('float64')):
                typ=sess._eval_name( 'float[8]', symbol=False )
            elif(dtyp == numpy.dtype('float32')):
                typ=sess._eval_name( 'float[4]', symbol=False )
            else:
                typ=sess._eval_name( 'anything' )

            L = list( a.flatten('F') )
            if(len(shp) == 1):
                return sess._eval_procedure_nowrap( 'Vector', len(L), L,
                    sess._eval_name("datatype") == typ
                )

            v = sess._eval_procedure_nowrap( 'Array', (1,...,len(L)), L,
                sess._eval_name("datatype") == typ
            )
            # Otherwise len(shp) > 1, build Array and alias to dimensions
            aa = sess._eval_name( 'ArrayTools:-Alias', wrap=False, symbol=False )
            w = sess._eval_procedure_nowrap( aa, sess._wrap(v), list(shp) )

            # If is 2-D, convert to Matrix
            if(len(shp) == 2):
                return sess._eval_procedure_nowrap( 'convert/Matrix', sess._wrap(w) )
            else:
                return w

        # Import mpmath expressions
        elif(mpmath is not None):
            if isinstance(a,mpmath.mpf):
                u = sess.execute( mpmath.nstr(a,n=mpmath.mp.dps) + ":" )
                return sess._unwrap( u )
            elif isinstance(a,mpmath.mpc):
                u = sess.execute( mpmath.nstr(a.real,n=mpmath.mp.dps) + ":" )
                v = sess.execute( mpmath.nstr(a.imag,n=mpmath.mp.dps) + ":" )
                return sess._unwrap( u + 1j * v )
            #elif isinstance(a,mpmath.matrix):
            else:
                raise NotImplementedError

        # Import pandas expressions
        elif(pandas is not None and isinstance(a,pandas.core.base.PandasObject)):
            if(isinstance(a,pandas.DataFrame)):
                # Convert underlying values to numpy to Matrix
                return sess._eval_procedure_nowrap( 'DataFrame', a.values, rows=list(a.index), columns=list(a.columns) )
            elif(isinstance(a,pandas.Series)):
                return sess._eval_procedure_nowrap( 'DataSeries', a.to_list(), labels=list(a.index) )
            else:
                raise NotImplementedError

        # Import PIL/Pillow expressions
        elif(PIL is not None and isinstance(a,PIL.Image.Image)):
            raise NotImplementedError

        # Import sympy expressions
        elif(sympy is not None and isinstance(a,sympy.Basic)):
            if(isinstance(a,sympy.Expr)):
                if(isinstance(a,sympy.Symbol)):
                    s = bytes( str(a), 'utf-8' )
                    return sess._maplec.ToMapleName( sess._kv, s, True )
                elif(isinstance(a,sympy.Number)): # Float, Rational, Integer
                    b = bytes( str(a) + ':', 'utf-8' )
                    return sess._maplec.EvalMapleStatement( sess._kv, b )
                elif(isinstance(a,sympy.NumberSymbol)):
                    if(str(a)=='Catalan'):
                        return sess._maplec.ToMapleName( sess._kv, b'Catalan', True )
                    elif(str(a)=='EulerGamma'):
                        return sess._maplec.ToMapleName( sess._kv, b'gamma', True )
                    elif(str(a)=='Exp1'):
                        return sess._maplec.EvalMapleStatement( sess._kv, b'exp(1):' )
                    elif(str(a)=='GoldenRatio'):
                        return sess._maplec.EvalMapleStatement( sess._kv, b'(sqrt(5)+1)/2:' )
                    elif(str(a)=='Pi'):
                        return sess._maplec.ToMapleName( sess._kv, b'Pi', True )
                    elif(str(a)=='TribonacciConstant'):
                        return sess._maplec.EvalMapleStatement( sess._kv, b'RootOf(_Z^3-_Z^2-_Z-1):' )
                    else:
                        raise NotImplementedError
                elif(isinstance(a,sympy.Add)):
                    (b, c) = a.as_two_terms()
                    return sess._eval_procedure_nowrap( '+', b, c )
                elif(isinstance(a,sympy.Mul )):
                    (b, c) = a.as_two_terms()
                    return sess._eval_procedure_nowrap( '*', b, c )
                elif(isinstance(a,sympy.Pow)):
                    (b, c) = a.as_base_exp()
                    return sess._eval_procedure_nowrap( '^', b, c )
                elif(isinstance(a,sympy.Function)):
                    sympy_fname = str(a.func)
                    if(sympy_fname == 'Id'):
                        raise NotImplementedError
                    elif(sympy_fname == 'Abs'): fname = 'abs'
                    elif(sympy_fname == 'ExprCondPair'): raise NotImplementedError
                    elif(sympy_fname == 'FallingFactorial'): raise NotImplementedError
                    elif(sympy_fname == 'HyperbolicFunction'): raise NotImplementedError
                    elif(sympy_fname == 'IdentityFunction'):
                        return sess._maplec.EvalMapleStatement( sess._kv, b'()->args:' )
                    elif(sympy_fname == 'LambertW'): fname = sympy_fname
                    elif(sympy_fname == 'Max'): fname = 'max'
                    elif(sympy_fname == 'Min'): fname = 'min'
                    elif(sympy_fname == 'MultiFactorial'): raise NotImplementedError
                    elif(sympy_fname == 'Piecewise'): raise NotImplementedError
                    elif(sympy_fname == 'RisingFactorial'): raise NotImplementedError
                    elif(sympy_fname == 'RoundFunction'): raise NotImplementedError
                    elif(sympy_fname == 'acos'): fname = 'arccos'
                    elif(sympy_fname == 'acosh'): fname = 'arccosh'
                    elif(sympy_fname == 'acot'): fname = 'arccot'
                    elif(sympy_fname == 'acoth'): fname = 'arccoth'
                    elif(sympy_fname == 'acsc'): fname = 'arccsc'
                    elif(sympy_fname == 'acsch'): fname = 'arccsch'
                    elif(sympy_fname == 'arg'): fname = 'argument'
                    elif(sympy_fname == 'asec'): fname = 'arcsec'
                    elif(sympy_fname == 'asech'): fname = 'arcsech'
                    elif(sympy_fname == 'asin'): fname = 'arcsin'
                    elif(sympy_fname == 'asinh'): fname = 'arcsinh'
                    elif(sympy_fname == 'atan'): fname = 'arctan'
                    elif(sympy_fname == 'atan2'): fname = 'arctan'
                    elif(sympy_fname == 'atanh'): fname = 'arctanh'
                    elif(sympy_fname == 'bell'): raise NotImplementedError
                    elif(sympy_fname == 'bernoulli'): raise NotImplementedError
                    elif(sympy_fname == 'binomial'): fname = sympy_fname
                    elif(sympy_fname == 'catalan'): raise NotImplementedError
                    elif(sympy_fname == 'cbrt'):
                        return sess._eval_procedure_nowrap( 'surd', a[0], 3, *(a.args[1:]) )
                    elif(sympy_fname == 'ceiling'): fname = 'ceil'
                    elif(sympy_fname == 'conjugate'): fname = sympy_fname
                    elif(sympy_fname == 'cos'): fname = sympy_fname
                    elif(sympy_fname == 'cosh'): fname = sympy_fname
                    elif(sympy_fname == 'cot'): fname = sympy_fname
                    elif(sympy_fname == 'coth'): fname = sympy_fname
                    elif(sympy_fname == 'csc'): fname = sympy_fname
                    elif(sympy_fname == 'csch'): fname = sympy_fname
                    elif(sympy_fname == 'euler'): raise NotImplementedError
                    elif(sympy_fname == 'exp'): fname = sympy_fname
                    elif(sympy_fname == 'exp_polar'): fname = 'exp'
                    elif(sympy_fname == 'factorial'): fname = sympy_fname
                    elif(sympy_fname == 'factorial2'): fname = 'doublefactorial'
                    elif(sympy_fname == 'fibonacci'): raise NotImplementedError
                    elif(sympy_fname == 'floor'): fname = sympy_fname
                    elif(sympy_fname == 'frac'): fname = sympy_fname
                    elif(sympy_fname == 'genocchi'): raise NotImplementedError
                    elif(sympy_fname == 'harmonic'): fname = sympy_fname
                    elif(sympy_fname == 'im'): fname = 'Im'
                    elif(sympy_fname == 'log'): fname = sympy_fname
                    elif(sympy_fname == 'lucas'): raise NotImplementedError
                    elif(sympy_fname == 'nC'): raise NotImplementedError
                    elif(sympy_fname == 'nP'): raise NotImplementedError
                    elif(sympy_fname == 'nT'): raise NotImplementedError
                    elif(sympy_fname == 'partition'): raise NotImplementedError
                    elif(sympy_fname == 'periodic_argument'): raise NotImplementedError
                    elif(sympy_fname == 'polar_lift'): raise NotImplementedError
                    elif(sympy_fname == 'principal_branch'): raise NotImplementedError
                    elif(sympy_fname == 're'): fname = 'Re'
                    elif(sympy_fname == 'real_root'): raise NotImplementedError
                    elif(sympy_fname == 'real_roots'):
                        sol = sess._eval_procedure('solve', *(a.args) )
                        return sess._eval_procedure_nowrap('[]', sol)
                    elif(sympy_fname == 'root'): raise NotImplementedError
                    elif(sympy_fname == 'sec'): fname = sympy_fname
                    elif(sympy_fname == 'sech'): fname = sympy_fname
                    elif(sympy_fname == 'sign'): fname = sympy_fname
                    elif(sympy_fname == 'sin'): fname = sympy_fname
                    elif(sympy_fname == 'sinc'): raise NotImplementedError
                    elif(sympy_fname == 'sinh'): fname = sympy_fname
                    elif(sympy_fname == 'sqrt'): fname = sympy_fname
                    elif(sympy_fname == 'stirling'): raise NotImplementedError
                    elif(sympy_fname == 'subfactorial'): raise NotImplementedError
                    elif(sympy_fname == 'tan'): fname = sympy_fname
                    elif(sympy_fname == 'tanh'): fname = sympy_fname
                    elif(sympy_fname == 'tribonacci'): raise NotImplementedError
                    else:
                        raise NotImplementedError
                    return sess._eval_procedure_nowrap( fname, *(a.args) )
                else:
                    raise NotImplementedError
            elif(isinstance(a,sympy.Rel)):
                u = sess._unwrap( a.lhs )
                v = sess._unwrap( a.rhs )
                if(isinstance(a,sympy.Equality)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'=', u, v )
                elif(isinstance(a,sympy.Unequality)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'<>', u, v )
                elif(isinstance(a,sympy.GreaterThan)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'>=', u, v )
                elif(isinstance(a,sympy.LessThan)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'<=', u, v )
                elif(isinstance(a,sympy.StrictGreaterThan)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'>', u, v )
                elif(isinstance(a,sympy.StrictLessThan)):
                    return sess._maplec.ToMapleRelation( sess._kv, b'<', u, v )
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        else: 
            raise RuntimeError
