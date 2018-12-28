import os
try:
    import multiprocessing  # NOQA: F401
except ImportError:
    pass
# nose requires multiprocessing and logging to be initialized before the setup
# call, or we'll get a spurious crash on exit.
from setuptools import setup, find_packages


# figure out what the install will need
INSTALL_REQUIRES = [
    "boto3",
    "python-json-logger",
    "retrying",
]
TESTS_REQUIRE = [
    "mock",
    "moto",
    "nose",
]


def read_text_file(fname):
    '''Utility function to read the README file.'''
    content = None
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        content = f.read()
    return content


setup(
    name="sqs-log-handler",
    version="1.1.0",
    author="Wei Liu",
    author_email="weil@zillowgroup.com",
    description="a python log handler that pushes logs into AWS sqs",
    license=read_text_file('LICENSE'),
    keywords="zillow",
    url="http://github.com/zillow/python-sqs-logging-handler",
    packages=find_packages(),
    long_description=read_text_file('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    test_suite="nose.collector",
)
