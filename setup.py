from distutils.core import setup

setup(
    name='LayoutEagle',
    version='0.1',
    packages=['layouteagle'],
    install_requires= open('requirements.txt').read().splitlines(),
    license='GPLv3',
    long_description=open('README.md').read()
)