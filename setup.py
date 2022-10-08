from setuptools import setup
from teapl.objects import ver
import os, shutil

shutil.rmtree("tmp", ignore_errors=True)
os.mkdir("tmp")
shutil.copy("teapl/main.py", "tmp/teapl")

setup(
   name='tea_pl',
   version=ver,
   description='TeaPL is a C-like programming language',
   author='NDRAEY',
   author_email='pikachu_andrey@vk.com',
   packages=['teapl'],
   scripts=['tmp/teapl']
)

shutil.rmtree("tmp")
