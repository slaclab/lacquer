from setuptools import setup, find_packages

requires = [
    'ply',
    'future'
]

setup(
    name='lacquer',
    version='0.0.1',
    packages=find_packages(),
    url='http://github.com/lsst-dm/lacquer',
    license='Apache',
    author='Brian Van Klaveren',
    author_email='bvan@slac.stanford.edu',
    description='lacquer: A SQL Parser based on the parser in presto (github.com/prestodb)',
    install_requires=requires,
    zip_safe=False
)
