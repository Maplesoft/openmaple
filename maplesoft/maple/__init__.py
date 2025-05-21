import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()
elif not (sys.version_info >= (3,8)):
    print("This script requires Python version >= 3.8")
    exit()

from maplesoft.maple.Expression import Expression
from maplesoft.maple.Session import Session
from maplesoft.maple.exportto import exportto
from maplesoft.maple.importfrom import importfrom

_activesession = Session()

def getactive():
    global _activesession
    return _activesession

def setactive(sess):
    global _activesession
    _activesession = sess

def eval(*args):
    global _activesession
    if(_activesession == None):
        raise RuntimeError('cannot establish a connection to Maple')
    return _activesession.eval(*args)

def execute(a):
    global _activesession
    if(_activesession == None):
        raise RuntimeError('cannot establish a connection to Maple')
    return _activesession.execute(a)

def range(a,b):
    global _activesession
    if(_activesession == None):
        raise RuntimeError('cannot establish a connection to Maple')
    return _activesession.range(a,b)

def symbol(a):
    global _activesession
    if(_activesession == None):
        raise RuntimeError('cannot establish a connection to Maple')
    return _activesession.symbol(a)

def symbols(*args):
    if(_activesession == None):
        raise RuntimeError('cannot establish a connection to Maple')
    return _activesession.symbols(*args)
