import sys

if not sys.argv[:-1]:
    print("Specify a file!")
    exit(1)

file = sys.argv[-1]

import subprocess as sp

proc = sp.call("python setup.py install", shell=True)
proc = sp.call(["teapl", file])
