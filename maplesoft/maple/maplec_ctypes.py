import ctypes
import sys

def textCallBack(data, tag, output):
    pass

def queryInterrupt( data ):
    pass

def errorCallBack( data, offset, msg ):
    raise Exception( msg.decode('utf-8') )

def callBackCallBack( data, output ):
    pass

def buildCallBackVector():
    c_textCallBack = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p )( textCallBack )
    c_errorCallBack = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_int64, ctypes.c_char_p )( errorCallBack )
    c_statusCallBack = 0
    c_readLineCallBack = 0
    c_redirectCallBack = 0
    c_streamCallBack = 0
    c_queryInterrupt = ctypes.CFUNCTYPE( ctypes.c_bool, ctypes.c_void_p )( queryInterrupt )
    c_callBackCallBack = ctypes.CFUNCTYPE( ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p )( callBackCallBack )
    mcbv = MCallBackVectorDesc(
        c_textCallBack,
        c_errorCallBack,
        c_statusCallBack,
        c_readLineCallBack,
        c_redirectCallBack,
        c_streamCallBack,
        c_queryInterrupt,
        c_callBackCallBack
    )
    return ctypes.pointer( mcbv )

class MCallBackVectorDesc(ctypes.Structure):
    _fields_ = [
        ("textCallBack", ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p ) ),
        ("errorCallBack", ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_int64, ctypes.c_char_p ) ),
        ("statusCallBack", ctypes.c_void_p),
        ("readLineCallBack", ctypes.c_void_p),
        ("redirectCallBack", ctypes.c_void_p),
        ("streamCallBack", ctypes.c_void_p),
        ("queryInterrupt", ctypes.CFUNCTYPE( ctypes.c_bool, ctypes.c_void_p ) ),
        ("callBackCallBack", ctypes.CFUNCTYPE( ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p ) )
    ]

def load_maplec(so_file):
    """load maplec from library and declare interface types for OpenMaple commands"""
    try:
        maplec = ctypes.CDLL(so_file)
    except OSError:
        return None

    MKernelVector = ctypes.c_void_p
    RTableSettings = ctypes.c_void_p
    ALGEB = ctypes.c_void_p

    # Export definitions
    maplec.EvalMapleProcedure.argtypes = [ MKernelVector, ALGEB, ALGEB ]
    maplec.EvalMapleProcedure.restype = ALGEB

    maplec.EvalMapleStatement.argtypes = [ MKernelVector, ctypes.c_char_p ]
    maplec.EvalMapleStatement.restype = ALGEB

    maplec.IsMapleAssignedName.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleAssignedName.restype = ctypes.c_bool

    maplec.IsMapleComplex64.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleComplex64.restype = ctypes.c_bool

    maplec.IsMapleComplexNumeric.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleComplexNumeric.restype = ctypes.c_bool

    maplec.IsMapleExpressionSequence.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleExpressionSequence.restype = ctypes.c_bool

    maplec.IsMapleFloat64.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleFloat64.restype = ctypes.c_bool

    maplec.IsMapleFraction.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleFraction.restype = ctypes.c_bool

    maplec.IsMapleInteger.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleInteger.restype = ctypes.c_bool

    maplec.IsMapleInteger64.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleInteger64.restype = ctypes.c_bool

    maplec.IsMapleList.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleList.restype = ctypes.c_bool

    maplec.IsMapleName.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleName.restype = ctypes.c_bool

    maplec.IsMapleNumeric.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleNumeric.restype = ctypes.c_bool

    maplec.IsMapleRTable.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleRTable.restype = ctypes.c_bool

    maplec.IsMapleSet.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleSet.restype = ctypes.c_bool

    maplec.IsMapleString.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleString.restype = ctypes.c_bool

    maplec.IsMapleTable.argtypes = [ MKernelVector, ALGEB ]
    maplec.IsMapleTable.restype = ctypes.c_bool

    maplec.MapleALGEB_SPrintf1.argtypes = [ MKernelVector, ctypes.c_char_p, ALGEB ]
    maplec.MapleALGEB_SPrintf1.restype = ALGEB

    maplec.MapleAssign.argtypes = [ MKernelVector, ALGEB, ALGEB ]
    maplec.MapleAssign.restype = ALGEB

    maplec.MapleEvalhf.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleEvalhf.restype = ctypes.c_double

    maplec.MapleExpseqAssign.argtypes = [ MKernelVector, ALGEB, ctypes.c_int, ALGEB ]
    maplec.MapleExpseqAssign.restype = None

    maplec.MapleExpseqSelect.argtypes = [ MKernelVector, ALGEB, ctypes.c_int ]
    maplec.MapleExpseqSelect.restype = ALGEB

    maplec.MapleGcAllow.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleGcAllow.restype = None

    maplec.MapleGcProtect.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleGcProtect.restype = None

    maplec.MapleListAlloc.argtypes = [ MKernelVector, ctypes.c_int ]
    maplec.MapleListAlloc.restype = ALGEB

    maplec.MapleListAssign.argtypes = [ MKernelVector, ALGEB, ctypes.c_int, ALGEB ]
    maplec.MapleListAssign.restype = None

    maplec.MapleListSelect.argtypes = [ MKernelVector, ALGEB, ctypes.c_int ]
    maplec.MapleListSelect.restype = ALGEB

    maplec.MapleNameValue.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleNameValue.restype = ALGEB

    maplec.MapleNumArgs.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleNumArgs.restype = ctypes.c_int

    maplec.MapleNumElements.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleNumElements.restype = ctypes.c_int

    maplec.MapleSelectImaginaryPart.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleSelectImaginaryPart.restype = ALGEB

    maplec.MapleSelectRealPart.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleSelectRealPart.restype = ALGEB

    maplec.MapleTableAlloc.argtypes = [ MKernelVector ]
    maplec.MapleTableAlloc.restype = ALGEB

    maplec.MapleTableAssign.argtypes = [ MKernelVector, ALGEB, ALGEB, ALGEB ]
    maplec.MapleTableAssign.restype = None

    maplec.MapleTableDelete.argtypes = [ MKernelVector, ALGEB, ALGEB ]
    maplec.MapleTableDelete.restype = None

    maplec.MapleTableHasEntry.argtypes = [ MKernelVector, ALGEB, ALGEB ]
    maplec.MapleTableHasEntry.restype = ctypes.c_bool

    maplec.MapleTableSelect.argtypes = [ MKernelVector, ALGEB, ALGEB ]
    maplec.MapleTableSelect.restype = ALGEB

    maplec.MapleToFloat64.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleToFloat64.restype = ctypes.c_double

    maplec.MapleToInteger64.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleToInteger64.restype = ctypes.c_int64

    maplec.MapleToM_BOOL.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleToM_BOOL.restype = ctypes.c_bool

    maplec.MapleToString.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleToString.restype = ctypes.c_char_p

    maplec.MapleUnique.argtypes = [ MKernelVector, ALGEB ]
    maplec.MapleUnique.restype = ALGEB

    maplec.NewMapleExpressionSequence.argtypes = [ MKernelVector, ctypes.c_int ]
    maplec.NewMapleExpressionSequence.restype = ALGEB

    maplec.RTableLowerBound.argtypes = [ MKernelVector, ALGEB, ctypes.c_int ]
    maplec.RTableLowerBound.restype = ctypes.c_int

    maplec.RTableUpperBound.argtypes = [ MKernelVector, ALGEB, ctypes.c_int ]
    maplec.RTableLowerBound.restype = ctypes.c_int

    maplec.RTableNumDimensions.argtypes = [ MKernelVector, ALGEB ]
    maplec.RTableNumDimensions.restype = ctypes.c_int

    maplec.StartMaple.argtypes = [ 
        ctypes.c_int,    # int argc
        ctypes.c_char_p, # char* argv
        ctypes.POINTER( MCallBackVectorDesc ), # MCallBackVector cb
        ctypes.c_void_p, # void *user_data
        ctypes.c_void_p, # void *info
        ctypes.c_char_p  # char *errstr
    ]
    maplec.StartMaple.restype = MKernelVector

    maplec.StopMaple.argtypes = [ MKernelVector ]
    maplec.StopMaple.restype = ctypes.c_void_p

    maplec.ToMapleBoolean.argtypes = [ MKernelVector, ctypes.c_int ]
    maplec.ToMapleBoolean.restype = ALGEB

    maplec.ToMapleComplex.argtypes = [ MKernelVector, ctypes.c_double, ctypes.c_double ]
    maplec.ToMapleComplex.restype = ALGEB

    maplec.ToMapleFloat.argtypes = [ MKernelVector, ctypes.c_double ]
    maplec.ToMapleFloat.restype = ALGEB

    maplec.ToMapleFraction.argtypes = [ MKernelVector, ctypes.c_int, ctypes.c_int ]
    maplec.ToMapleFraction.restype = ALGEB

    maplec.ToMapleInteger.argtypes = [ MKernelVector, ctypes.c_int64 ]
    maplec.ToMapleInteger.restype = ALGEB

    maplec.ToMapleName.argtypes = [ MKernelVector, ctypes.c_char_p, ctypes.c_bool ]
    maplec.ToMapleName.restype = ALGEB

    maplec.ToMapleRelation.argtypes = [ MKernelVector, ctypes.c_char_p, ALGEB, ALGEB ]
    maplec.ToMapleRelation.restype = ALGEB

    maplec.ToMapleString.argtypes = [ MKernelVector, ctypes.c_char_p ]
    maplec.ToMapleString.restype = ALGEB

    maplec.ToMapleUneval.argtypes = [ MKernelVector, ALGEB ]
    maplec.ToMapleUneval.restype = ALGEB

    return maplec

def char_pointer():
    return ctypes.c_char_p()

def create_string():
    return ctypes.create_string_buffer(1024)

def callback_test():
    return ctypes.CFUNCTYPE( ctypes.c_int, ctypes.c_char_p );
