import os
import subprocess as sp

codes = []

for currentdir, dirs, files in os.walk("examples/"):
    for i in files:
        proc = sp.Popen(['python3', 'teapl/main.py', "examples/"+i], stdout=sp.PIPE)
        proc.wait()

        code = proc.returncode

        print("TEST", i, "=> ", end='')

        if code == 0:
            print("\x1b[32mOK\x1b[0m")
        else:
            print("\x1b[31mERROR\x1b[0m")

        os.remove(i.split(".")[0])
