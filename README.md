# Log handler that forwards log message to AWS SQS

This log handler pushes log messages to AWS SQS so downstream processors
can consume (e.g. push them into Splunk).

See its [`log4j` equivalent](https://github.com/zillow/sqs-log4j-handler) for more details

For Splunk, this log handler should be combined with [json log formatter](https://pypi.python.org/pypi/JSON-log-formatter/0.0.2).

## Local Development & Running Tests

** prerequisites: **
- [pipenv](https://pipenv.readthedocs.io/en/latest/)

Create a virtual environment with `pipenv` and run the tests like this:
```
$ pipenv install --dev
$ pipenv shell
(python-sqs-logging-handler) $ pytest
```
 