#!/usr/bin/python3

import sys, os
try:
    from teapl import tokenizer, action, objects, pretty
    from teapl.objects import ver
    from teapl import expression as expr
    from teapl.codegen import codegen
except:
    import tokenizer, action, objects, pretty
    from objects import ver
    import expression as expr
    from codegen import codegen
    import findcompiler as compiler
    '''
    print(f"TeaPL module is not installed. Run 'python3 setup.py install' first!")
    exit(1)
    '''
import subprocess as sp
import time
from pprint import pprint

defines = '''
typedef unsigned int uint;
typedef size_t isize;
'''

def parse_code(code: str) -> tuple[list[objects.Token], list[objects.Token]]:
    tokenized = orig = tokenizer.tokenize(code)
    tokenized = pretty.pretty(tokenized, orig)
    tokenized = pretty.remove_whitespaces(tokenized)
    tokenized = expr.parse_expressions(tokenized, orig)
    tokenized = expr.parse_comprasions(tokenized, orig)
    tokenized = pretty.build_arrays(tokenized, orig)
    tokenized = pretty.build_indexes(tokenized, orig)
    tokenized = pretty.build_funccalls(tokenized, orig)
    return tokenized, orig

def make_actions(tokens, orig: list[objects.Token, ...]) -> list[action.Action]:
    actions = action.make_actions(tokenized, orig)
    return actions

print(f"The TeaPL Project [v{ver}]\n")

if not sys.argv[1:]:
    print("Specify a file! Exiting...")
    exit(1)

fname = sys.argv[-1]

code = open(fname).read()
starttime = time.time()
tokenized, origtokens = parse_code(code)
pprint(tokenized)
print()
actions = make_actions(tokenized, origtokens)
pprint(actions)
print()
code = codegen(actions)
code = "#include <stdio.h>\n"+defines+code
print(code)

ofname = '.'.join(sys.argv[-1].split("/")[-1].split(".")[:-1])

with open(ofname+".c", "w") as outfile:
    outfile.write(code)
    outfile.close()

print("Found compiler:", compiler.find())

compiler = sp.Popen([compiler.find(), '-x', 'c', '-Wall', '-std=c99', ofname+".c", '-o', ofname])
# compiler = sp.Popen(['clang', '-x', 'c', '-w', ofname+".c", '-o', ofname])
compiler.wait()

os.remove(ofname+".c")

print("\rDone %.2fs\033[K\n"%(time.time()-starttime),end='')
