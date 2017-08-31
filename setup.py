import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='postman_problems',
    version='0.1dev',
    author='Andrew Brooks',
    author_email='andrewbrooks@gmail.com',
    description='Solutions to Postman graph optimization problems: Chinese and Rural Postman problems',
    license='MIT License',
    keywords='chinese postman problem networkx optimization network graph arc routing',
    url='https://github.com/brooksandrew',
    packages=['postman_problems'],
    long_description=read('README_reference.md'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'numpy',
        'pandas',
        'networkx',
        'imageio'
    ],
    entry_points={
        'console_scripts': ['chinese_postman=postman_problems.main:main'],
    }
)

