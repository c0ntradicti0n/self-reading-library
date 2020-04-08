from distutils.core import setup

setup(
    name='LayoutEagle',
    version='0.1',
    packages=['layouteagle', ( open('requirements.txt').read().split("/n"))],
    license='GPLv3',
    long_description=open('README.md').read()
)