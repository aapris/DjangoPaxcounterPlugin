import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-paxcounter-plugin',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A plugin for Django Plugindemo to receive and store Paxcounter MAC address data.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://www.example.com/',
    author='Aapo Rista',
    author_email='aapris@gmail.com',
    scripts=['paxcounter/paxcounter_readserial.py', ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
