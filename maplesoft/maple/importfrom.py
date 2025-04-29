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
                    match(str(a)):
                        case 'Catalan':
                            return sess._maplec.ToMapleName( sess._kv, b'Catalan', True )
                        case 'EulerGamma':
                            return sess._maplec.ToMapleName( sess._kv, b'gamma', True )
                        case 'Exp1':
                            return sess._maplec.EvalMapleStatement( sess._kv, b'exp(1):' )
                        case 'GoldenRatio':
                            return sess._maplec.EvalMapleStatement( sess._kv, b'(sqrt(5)+1)/2:' )
                        case 'Pi':
                            return sess._maplec.ToMapleName( sess._kv, b'Pi', True )
                        case 'TribonacciConstant':
                            return sess._maplec.EvalMapleStatement( sess._kv, b'RootOf(_Z^3-_Z^2-_Z-1):' )
                        case _:
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
                    match sympy_fname:

                        case 'Id': raise NotImplementedError
                        case 'Abs': fname = 'abs'
                        case 'ExprCondPair': raise NotImplementedError
                        case 'FallingFactorial': raise NotImplementedError
                        case 'HyperbolicFunction': raise NotImplementedError
                        case 'IdentityFunction':
                            return sess._maplec.EvalMapleStatement( sess._kv, b'()->args:' )
                        case 'LambertW': fname = sympy_fname
                        case 'Max': fname = 'max'
                        case 'Min': fname = 'min'
                        case 'MultiFactorial': raise NotImplementedError
                        case 'Piecewise': raise NotImplementedError
                        case 'RisingFactorial': raise NotImplementedError
                        case 'RoundFunction': raise NotImplementedError
                        case 'acos': fname = 'arccos'
                        case 'acosh': fname = 'arccosh'
                        case 'acot': fname = 'arccot'
                        case 'acoth': fname = 'arccoth'
                        case 'acsc': fname = 'arccsc'
                        case 'acsch': fname = 'arccsch'
                        case 'arg': fname = 'argument'
                        case 'asec': fname = 'arcsec'
                        case 'asech': fname = 'arcsech'
                        case 'asin': fname = 'arcsin'
                        case 'asinh': fname = 'arcsinh'
                        case 'atan': fname = 'arctan'
                        case 'atan2': fname = 'arctan'
                        case 'atanh': fname = 'arctanh'
                        case 'bell': raise NotImplementedError
                        case 'bernoulli': raise NotImplementedError
                        case 'binomial': fname = sympy_fname
                        case 'catalan': raise NotImplementedError
                        case 'cbrt':
                            return sess._eval_procedure_nowrap( 'surd', a[0], 3, *(a.args[1:]) )
                        case 'ceiling': fname = 'ceil'
                        case 'conjugate': fname = sympy_fname
                        case 'cos': fname = sympy_fname
                        case 'cosh': fname = sympy_fname
                        case 'cot': fname = sympy_fname
                        case 'coth': fname = sympy_fname
                        case 'csc': fname = sympy_fname
                        case 'csch': fname = sympy_fname
                        case 'euler': raise NotImplementedError
                        case 'exp': fname = sympy_fname
                        case 'exp_polar': fname = 'exp'
                        case 'factorial': fname = sympy_fname
                        case 'factorial2': fname = 'doublefactorial'
                        case 'fibonacci': raise NotImplementedError
                        case 'floor': fname = sympy_fname
                        case 'frac': fname = sympy_fname
                        case 'genocchi': raise NotImplementedError
                        case 'harmonic': fname = sympy_fname
                        case 'im': fname = 'Im'
                        case 'log': fname = sympy_fname
                        case 'lucas': raise NotImplementedError
                        case 'nC': raise NotImplementedError
                        case 'nP': raise NotImplementedError
                        case 'nT': raise NotImplementedError
                        case 'partition': raise NotImplementedError
                        case 'periodic_argument': raise NotImplementedError
                        case 'polar_lift': raise NotImplementedError
                        case 'principal_branch': raise NotImplementedError
                        case 're': fname = 'Re'
                        case 'real_root': raise NotImplementedError
                        case 'real_roots':
                            sol = sess._eval_procedure('solve', *(a.args) )
                            return sess._eval_procedure_nowrap('[]', sol)
                        case 'root': raise NotImplementedError
                        case 'sec': fname = sympy_fname
                        case 'sech': fname = sympy_fname
                        case 'sign': fname = sympy_fname
                        case 'sin': fname = sympy_fname
                        case 'sinc': raise NotImplementedError
                        case 'sinh': fname = sympy_fname
                        case 'sqrt': fname = sympy_fname
                        case 'stirling': raise NotImplementedError
                        case 'subfactorial': raise NotImplementedError
                        case 'tan': fname = sympy_fname
                        case 'tanh': fname = sympy_fname
                        case 'tribonacci': raise NotImplementedError
                        case _: raise NotImplementedError
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
