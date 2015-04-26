
from setuptools import setup

setup(
    name='DbMake',
    version='1.0',
    py_modules=['dbmake'],
    install_requires=['psycopg2'],
    entry_points='''
        [console_scripts]
        dbmake=dbmake.py
    '''
)