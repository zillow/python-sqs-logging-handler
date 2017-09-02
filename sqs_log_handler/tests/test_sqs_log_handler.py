import logging
import time

import boto3

import unittest

from moto import mock_sqs
from mock import Mock, patch

from pythonjsonlogger import jsonlogger
from sqs_log_handler import sqsloghandler

# mock time value and functions
mock_time_tuple = (2016, 1, 1, 0, 0, 0, 0, 0, 0)
mock_time_provider = Mock()
mock_time_provider.return_value = mock_time_tuple
mock_time = Mock()
mock_time.return_value = time.mktime(mock_time_tuple)

@mock_sqs
class TestSQSLogHandler(unittest.TestCase):
    def setUp(self):
        # create mock sqs queue
        self.log_queue_name = 'logging-queue-test'
        client = boto3.resource('sqs', aws_access_key_id='aws_key_id', aws_secret_access_key='secret_key', region_name='us-west-2')
        self.queue = client.create_queue(QueueName=self.log_queue_name)
        self.assertIsNotNone(self.queue)

        # set up the test target (log handler) together with a formatter.
        self.log_handler = sqsloghandler.SQSHandler(self.log_queue_name)
        formatter = jsonlogger.JsonFormatter('%(asctime) %(levelname) %(message)')
        self.log_handler.setFormatter(formatter)
        self.logger = logging.getLogger(TestSQSLogHandler.__name__)
        self.logger.addHandler(self.log_handler)

    def tearDown(self):
        self.queue.purge()

    @patch('time.time', mock_time)
    def test_sqs_log_handler_basic_json_format(self):
        """Fails if log handler does not output expected log message"""
        try:
            self.logger.info("test info message")
            body = self.retrieve_message()
            expected = ("""{"asctime": "2016-01-01 00:00:00,000","""
                        """ "levelname": "INFO", "message": "test info message"}""")
        except BaseException as err:
            self.fail("Should not raise exception, got {} instead".format(err))
        self.assertEqual(body, expected)

    @patch('time.time', mock_time)
    def test_sqs_log_handler_extra_json_data(self):
        """Fails if log handler does not output expected log message with extras"""
        try:
            extra = {
                "test": "test logging",
                "num": 1,
                5: "9",
                "float": 1.75,
                "nested": {"more": "data"}
            }
            self.logger.info("test info message with properties", extra=extra)
            body = self.retrieve_message()
            expected = ("""{"asctime": "2016-01-01 00:00:00,000", "levelname": "INFO","""
                        """ "message": "test info message with properties","""
                        """ "5": "9", "float": 1.75, "num": 1,"""
                        """ "test": "test logging", "nested": {"more": "data"}}""")
        except BaseException as err:
            self.fail("Should not raise exception, got {} instead".format(err))
        self.assertEqual(body, expected)

    @patch('time.time', mock_time)
    def test_sqs_log_handler_error(self):
        """Fails if log handler does not output expected log message at error level"""
        try:
            extra = {
                "test": "test logging",
                "num": 1,
                5: "9",
                "float": 1.75,
                "nested": {"more": "data"}
            }
            self.logger.error("test info message with properties", extra=extra)
            body = self.retrieve_message()
            expected = ("""{"asctime": "2016-01-01 00:00:00,000", "levelname": "ERROR","""
                        """ "message": "test info message with properties","""
                        """ "5": "9", "float": 1.75, "num": 1,"""
                        """ "test": "test logging", "nested": {"more": "data"}}""")
        except BaseException as err:
            self.fail("Should not raise exception, got {} instead".format(err))
        self.assertEqual(body, expected)

    @patch('time.time', mock_time)
    def test_sqs_log_global_extra(self):
        """Fails if log handler does not output expected log message at error level"""
        try:
            extra = {
                "test": "test logging",
                "num": 1,
                5: "9",
                "float": 1.75,
                "nested": {"more": "data"}
            }

            global_extra = {
                "cluster_name": "regression",
                "node_name": "localhost",
            }

            log_handler = sqsloghandler.SQSHandler(self.log_queue_name, global_extra=global_extra)
            formatter = jsonlogger.JsonFormatter('%(asctime) %(levelname) %(message)')
            log_handler.setFormatter(formatter)
            logger = logging.getLogger(TestSQSLogHandler.__name__ + "global-extra")
            logger.addHandler(log_handler)

            logger.error("test info message with properties", extra=extra)
            body = self.retrieve_message()
            expected = ("""{"asctime": "2016-01-01 00:00:00,000", "levelname": "ERROR","""
                        """ "message": "test info message with properties", "5": "9", """
                        """"float": 1.75, "num": 1, "cluster_name": "regression","""
                        """ "test": "test logging", "nested": {"more": "data"}, "node_name": "localhost"}""")
        except BaseException as err:
            self.fail("Should not raise exception, got {} instead".format(err))
        self.assertEqual(body, expected)

    def retrieve_message(self):
        messages = list(self.queue.receive_messages())
        self.assertGreater(messages.count, 0, "must have at least one message")
        return messages[0].body