from setuptools import setup

setup(
    name='LayoutEagle',
    version='0.1',
    packages=['core'],
    install_requires= open('requirements.txt').read().splitlines(),
    license='GPLv3',
    long_description=open('README.md').read()
)