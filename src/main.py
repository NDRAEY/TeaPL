#!/usr/bin/python3

import tokenizer
import action
import pretty
import expression as expr
from codegen import codegen
import sys
import subprocess as sp
import time
from pprint import pprint

ver = "1.1"

print(f"The Charmeleon Project [v{ver}]\n")

if not sys.argv[1:]:
    print("Specify a file! Exiting...")
    exit(1)

fname = sys.argv[-1]

code = open(fname).read()
starttime = time.time()
tokenized = orig = tokenizer.tokenize(code)
tokenized = pretty.pretty(tokenized, orig)
tokenized = pretty.remove_whitespaces(tokenized)
tokenized = expr.parse_expressions(tokenized, orig)
tokenized = expr.parse_comprasions(tokenized, orig)
pprint(tokenized)
print()
actions = action.make_actions(tokenized, orig)
print()
pprint(actions)
print()
code = codegen(actions)
print(code)

print("\rCompiling...\033[K", end='')
gcc = sp.Popen(['clang','-x','c','-o',sys.argv[-1].split(".")[0],'-'], stdin=sp.PIPE)
gcc.stdin.write(bytes(code, 'utf-8'))
gcc.stdin.close()
gcc.wait()
print("\rDone %.2fs\033[K\n"%(time.time()-starttime),end='')
