from setuptools import setup, find_packages

setup(
    name = "gerobak",
    version = "0.1.0",
    url = 'http://gerobak.dahsy.at/',
    license = 'AGPL',
    description = 'Gerobak - bukan apt-web kaleee!',
    author = 'Fajran Iman Rusadi',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'django-registration', 'simplejson'],
)

