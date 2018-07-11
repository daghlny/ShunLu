
import sys
import os

DEBUG = 0
ERROR = 1
logfile = object
logthreshold = 0

def initlog(_path, _threshold):
    logfile = open(_path, 'w')
    logthreshold = _threshold


def writelog(level, errormsg):
    if level >= logthreshold:
        logfile.write(errormsg)