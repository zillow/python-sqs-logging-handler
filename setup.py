import os
import logging
import sys
try:
    import multiprocessing
except:
    pass
# nose requires multiprocessing and logging to be initialized before the setup
# call, or we'll get a spurious crash on exit.
from setuptools import setup, find_packages
from setuptools.dist import Distribution


def read(fname):
    '''Utility function to read the README file.'''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# figure out what the install will need
install_requires = ["setuptools >=0.5", "python-json-logger", "boto3", "retrying"]

setup(
    name="sqs-log-handler",
    version="1.0",
    author="Wei Liu",
    author_email="weil@zillowgroup.com",
    description="a python log handler that pushes logs into AWS sqs",
    license="(C) Zillow, Inc. 2012-",
    keywords="zillow",
    url="http://github.com/zillow/python-sqs-logging-handler",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
    ],
    install_requires=install_requires,
    tests_require=["Nose >=1.1.2",
                   "mock >=0.7.2",
                   "NoseXUnit"] + install_requires,
    test_suite="nose.collector"
    )
