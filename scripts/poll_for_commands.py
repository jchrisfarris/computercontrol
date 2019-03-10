#!/usr/bin/env python

from __future__ import print_function

import boto3
from botocore.exceptions import ClientError
import json
import os
import time
import datetime
from dateutil import tz

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)

POLL_INTERVAL = 10
DEFAULT_REGION = "us-east-1"

COMMAND_MAP = {
    "mute": "sudo /rm17/cc/scripts/mute.sh",
    "sleep": "sudo /rm17/cc/scripts/sleep.sh"
}


def main(args, logger):
    config = load_config(args.config)

    sqs_client = boto3.client('sqs',
        aws_access_key_id = config['KEYID'],
        aws_secret_access_key = config['SECRETKEY'],
        region_name = config['REGION'])

    # Infinite Loop
    while True:
        command, ReceiptHandle = poll_for_command(config['SQSQUEUEURL'], sqs_client)
        if command is not None:
            if execute_command(command):
                delete_message(config['SQSQUEUEURL'], sqs_client, ReceiptHandle)
            else:
                logger.error("Failed to execute command {} for handle {}".format(command, ReceiptHandle))

        time.sleep(POLL_INTERVAL)
# end main


def poll_for_command(queue_url, sqs_client):

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=1,
        VisibilityTimeout=20,
        WaitTimeSeconds=10
    )

    # Returned Data:
    # {
    #   "Messages": [
    #     {
    #       "Attributes": {
    #         "ApproximateFirstReceiveTimestamp": "1552227122408",
    #         "ApproximateReceiveCount": "14",
    #         "SenderId": "AROABLAHV6:computercontrol-skill-endpoint",
    #         "SentTimestamp": "1552227122408"
    #       },
    #       "Body": "{\"command\": \"mute\"}",
    #       "MD5OfBody": "23cBLAH53",
    #       "MessageId": "78c4a70a-BLAH-4f6d416f369f",
    #       "ReceiptHandle": "AQEB2vBLAHBLAH+IskR"
    #     }
    #   ],
    #   "ResponseMetadata": {
    #     "HTTPHeaders": {
    #       "content-length": "1290",
    #       "content-type": "text/xml",
    #       "date": "Sun, 10 Mar 2019 14:16:53 GMT",
    #       "x-amzn-requestid": "2c80a2cf-BLAH-f6303744dabe"
    #     },
    #     "HTTPStatusCode": 200,
    #     "RequestId": "2c80a2cf-BLAH-f6303744dabe",
    #     "RetryAttempts": 0
    #   }
    # }

    logger.debug(json.dumps(response, sort_keys=True))

    if 'Messages' in response and len(response['Messages']) > 0 :
        body = json.loads(response['Messages'][0]['Body'])
        logger.info("Got command: {}".format(body))
        return(body, response['Messages'][0]['ReceiptHandle'])

    return(None, None)

def delete_message(queue_url, sqs_client, ReceiptHandle):
    response = sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=ReceiptHandle
    )
    logger.debug("Delete Response: {}".format(json.dumps(response, sort_keys=True)))


def load_config(config_file):
    config = {}

    # Validate Config Exists
    if not os.path.isfile(config_file):
        logger.critical("Cannot find config file {}. Aborting...".format(config_file))
        exit(1)

    # Open file
    with open(config_file, "r") as file:
        data = file.readlines()
        # Parse into Dict
        for line in data:
            key,value = line.split("=")
            config[key] = value.replace("\n", "")

    if 'REGION' not in config:
        config['REGION'] = DEFAULT_REGION

    return(config)


def execute_command(body):
    command = body['command']

    if command in COMMAND_MAP:
        logger.info("Executing {} : {}".format(command, COMMAND_MAP[command]))
        rc = os.system(COMMAND_MAP[command])
        if rc == 0:
            return(True)
        else:
            return(False) # message is not deleted from queue
    else:
        logger.error("Unknown Command {}".format(command))
        # Return True to delete the message.
        return(True)


if __name__ == '__main__':

    # Process Arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="print debugging info", action='store_true')
    parser.add_argument("--error", help="print error info only", action='store_true')
    parser.add_argument("--config", help="config file path", required=True)

    args = parser.parse_args()

    # Logging idea stolen from: https://docs.python.org/3/howto/logging.html#configuring-logging
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    if args.debug:
        ch.setLevel(logging.DEBUG)
    elif args.error:
        ch.setLevel(logging.ERROR)
    else:
        ch.setLevel(logging.INFO)
    # create formatter
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    # logger.setLevel(logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


    # Wrap in a handler for Ctrl-C
    try:
        rc = main(args, logger)
    except KeyboardInterrupt:
        exit(0)