import os
from setuptools import setup, find_packages


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level README file and 2) it's easier to
    type in the README file than to put a raw string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='postman_problems',
    version='0.1',
    author='Andrew Brooks',
    author_email='andrewbrooks@gmail.com',
    description='Solutions to Postman graph optimization problems: Chinese and Rural Postman problems',
    license='MIT License',
    keywords='chinese postman problem networkx optimization network graph arc routing',
    url='https://github.com/brooksandrew/postman_problems',
    download_url='https://github.com/brooksandrew/postman_problems/archive/v0.1.tar.gz',
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License'
    ],
    package_data={
        'postman_problems': [
            'postman_problems/examples/sleeping_giant/edgelist_sleeping_giant.csv',
            'postman_problems/examples/sleeping_giant/nodelist_sleeping_giant.csv',
            'postman_problems/examples/seven_bridges/edgelist_seven_bridges.csv'
        ]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'chinese_postman=postman_problems.chinese_postman:main',
            'chinese_postman_sleeping_giant=postman_problems.examples.sleeping_giant.cpp_sleeping_giant:main',
            'chinese_postman_seven_bridges=postman_problems.examples.seven_bridges.cpp_seven_bridges:main'
        ]
    },
    python_requires='>=2.7',
    install_requires=[
        'pandas',
        'networkx'
    ],
    extras_require={
        'viz': ['imageio', 'matplotlib', 'graphviz', 'tqdm'],
        'test': ['pytest', 'pytest-cov', 'pytest-console-scripts']
    }
)

