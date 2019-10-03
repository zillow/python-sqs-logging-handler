import json
import logging
import os
import time
import uuid

import boto3
import pytest

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

TEST_AWS_ACCESS_KEY_ID = 'aws_key_id'
TEST_AWS_SECRET_ACCESS_KEY = 'aws_secret_key'
TEST_AWS_DEFAULT_REGION = 'us-west-2'
os.environ['AWS_ACCESS_KEY_ID'] = TEST_AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = TEST_AWS_SECRET_ACCESS_KEY
os.environ['AWS_DEFAULT_REGION'] = TEST_AWS_DEFAULT_REGION

TEST_QUEUE_NAME = 'test-queue'
TEST_LOGGER_NAME = 'test-queue-logger'


@pytest.fixture
def logger_name():
    return '{}-{}'.format(TEST_LOGGER_NAME, str(uuid.uuid4()))


@pytest.fixture
def queue_name():
    return '{}-{}'.format(TEST_QUEUE_NAME, str(uuid.uuid4()))


@pytest.fixture
def sqs_client():
    # activate mock SQS
    mock_sqs_ctx = mock_sqs()
    mock_sqs_ctx.start()
    # SQS.ServiceResource
    client = boto3.resource('sqs')
    yield client
    # stop mock SQS
    mock_sqs_ctx.stop()


@pytest.fixture
def sqs_queue(sqs_client, queue_name):
    # sqs.Queue
    queue = sqs_client.create_queue(QueueName=queue_name)
    yield queue
    queue.purge()


@pytest.fixture
def sqs_logger(sqs_queue, queue_name, logger_name):
    if queue_name not in sqs_queue.url:
        err_msg = '{} not in QueueUrl={}'.format(queue_name, sqs_queue.url)
        raise ValueError(err_msg)

    # logger
    log_handler = sqsloghandler.SQSHandler(queue_name)
    formatter = jsonlogger.JsonFormatter('%(asctime) %(levelname) %(message)')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(log_handler)
    yield logger


def fetch_sqs_message(queue):
    messages = list(queue.receive_messages())
    messages_count = len(messages)
    assert messages_count > 0, "must have at least one message"
    return messages[0].body


@patch('time.time', mock_time)
def test_basic_operation(sqs_queue, sqs_logger):
    # set logger level
    sqs_logger.setLevel(logging.WARNING)

    # log a test message
    test_msg = 'test error message'
    sqs_logger.error(test_msg)

    # fetch message from queue
    found_str = fetch_sqs_message(sqs_queue)
    assert isinstance(found_str, str)

    # verify message content
    result_dict = json.loads(found_str)
    assert isinstance(result_dict, dict)
    expected_dict = {
        'asctime': '2016-01-01 00:00:00,000',
        'levelname': 'ERROR',
        'message': test_msg,
    }
    assert result_dict == expected_dict


@patch('time.time', mock_time)
def test_info_extra(sqs_queue, sqs_logger):
    # set logger level
    sqs_logger.setLevel(logging.INFO)

    # extra information
    extra_dict = {
        "test": "test logging",
        "num": 1,
        5: "9",
        "float": 1.75,
        "nested": {"more": "data"}
    }

    # log a test message
    test_msg = 'test info extra'
    sqs_logger.info(test_msg, extra=extra_dict)

    # fetch message from queue
    found_str = fetch_sqs_message(sqs_queue)
    assert isinstance(found_str, str)

    # verify message content
    result_dict = json.loads(found_str)
    assert isinstance(result_dict, dict)
    expected_dict = {
        'asctime': '2016-01-01 00:00:00,000',
        'levelname': 'INFO',
        'message': test_msg,
    }
    expected_dict.update({str(k): v for k, v in extra_dict.items()})
    assert result_dict == expected_dict


@patch('time.time', mock_time)
def test_error_extra(sqs_queue, sqs_logger):
    # set logger level
    sqs_logger.setLevel(logging.ERROR)

    # extra information
    extra_dict = {
        "test": "test logging",
        "num": 1,
        5: "9",
        "float": 1.75,
        "nested": {"more": "data"}
    }

    # log a test message
    test_msg = 'test error extra'
    sqs_logger.error(test_msg, extra=extra_dict)

    # fetch message from queue
    found_str = fetch_sqs_message(sqs_queue)
    assert isinstance(found_str, str)

    # verify message content
    result_dict = json.loads(found_str)
    assert isinstance(result_dict, dict)
    expected_dict = {
        'asctime': '2016-01-01 00:00:00,000',
        'levelname': 'ERROR',
        'message': test_msg,
    }
    expected_dict.update({str(k): v for k, v in extra_dict.items()})
    assert result_dict == expected_dict


@patch('time.time', mock_time)
def test_info_global_extra(sqs_queue, queue_name, logger_name):
    # global extra information
    global_extra_dict = {
        "cluster_name": "regression",
        "node_name": "localhost",
    }

    # sqs_logger
    log_handler = sqsloghandler.SQSHandler(queue_name, global_extra=global_extra_dict)
    formatter = jsonlogger.JsonFormatter('%(asctime) %(levelname) %(message)')
    log_handler.setFormatter(formatter)
    sqs_logger = logging.getLogger(logger_name)
    sqs_logger.addHandler(log_handler)

    # set logger level
    sqs_logger.setLevel(logging.INFO)

    # extra information
    extra_dict = {
        "test": "test logging global_extra",
        "num": 1,
        5: "9",
        "float": 1.75,
        "nested": {"more": "data"}
    }

    # log a test message
    test_msg = 'test info global_extra'
    sqs_logger.info(test_msg, extra=extra_dict)

    # fetch message from queue
    found_str = fetch_sqs_message(sqs_queue)
    assert isinstance(found_str, str)

    # verify message content
    result_dict = json.loads(found_str)
    assert isinstance(result_dict, dict)
    expected_dict = {
        'asctime': '2016-01-01 00:00:00,000',
        'levelname': 'INFO',
        'message': test_msg,
    }
    expected_dict.update({str(k): v for k, v in extra_dict.items()})
    expected_dict.update({str(k): v for k, v in global_extra_dict.items()})
    assert result_dict == expected_dict
