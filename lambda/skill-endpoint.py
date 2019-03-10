# -*- coding: utf-8 -*-
#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#

# This is a skill for getting device address.
# The skill serves as a simple sample on how to use the
# service client factory and Alexa APIs through the SDK.

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from ask_sdk_model import ui


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

sb = CustomSkillBuilder(api_client=DefaultApiClient())

WELCOME = ("Welcome to the Control Leo's Computer Skill!  "
           "You can issue commands to tell it to sleep or mute the volume. What do you want to do?")
WHAT_DO_YOU_WANT = "What do you want to do?"
ERROR = "Uh Oh. Looks like something went wrong."
MESSAGE_SENT = "Message sent to Leo's computer"
GOODBYE = "Bye! Thanks for using the Control Computer Skill!"
UNHANDLED = "This skill doesn't support that. Please ask something else"
HELP = ("You can use this skill by asking something like: "
        "whats my address?")

# permissions = ["read::alexa:device:all:address"]
# Location Consent permission to be shown on the card. More information
# can be checked at
# https://developer.amazon.com/docs/custom-skills/device-address-api.html#sample-response-with-permission-card


class LaunchRequestHandler(AbstractRequestHandler):
    # Handler for Skill Launch
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(WELCOME).ask(WHAT_DO_YOU_WANT)
        return handler_input.response_builder.response


class SleepIntentHandler(AbstractRequestHandler):
    # Send an SQS Message telling the computer to sleep
    def can_handle(self, handler_input):
        return is_intent_name("SleepIntent")(handler_input)

    def handle(self, handler_input):
        command = "sleep"
        card_text = "Leo's computer should go to sleep shortly"
        return(command_handler(command, handler_input, card_text))


class MuteIntentHandler(AbstractRequestHandler):
    # Send an SQS Message telling the computer to mute volume
    def can_handle(self, handler_input):
        return is_intent_name("MuteIntent")(handler_input)

    def handle(self, handler_input):
        command = "mute"
        card_text = "Leo's volume should be muted"
        return(command_handler(command, handler_input, card_text))

class SessionEndedRequestHandler(AbstractRequestHandler):
    # Handler for Session End
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    # Handler for Help Intent
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(HELP).ask(HELP)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    # Single handler for Cancel and Stop Intent
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        handler_input.response_builder.speak(GOODBYE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    # AMAZON.FallbackIntent is only available in en-US locale.
    # This handler will not be triggered except in that locale,
    # so it is safe to deploy on any locale
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(UNHANDLED).ask(HELP)
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    # Catch all exception handler, log exception and
    # respond with custom message
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.critical("Encountered following exception: {}".format(exception))

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


def command_handler(command, handler_input, card_text):
    req_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    service_client_fact = handler_input.service_client_factory
    sqs_client = boto3.client('sqs')

    try:
        logger.info(f"Sending the {command} Command")

        body = {'command': command }

        response = sqs_client.send_message(QueueUrl=os.environ['SQS_QUEUE'], MessageBody=json.dumps(body))
        logger.debug(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            response_builder.speak(MESSAGE_SENT)
            response_builder.set_card(
                ui.StandardCard(
                    title="Message Sent",
                    text=card_text,
                    # image=ui.Image(
                    #     small_image_url="<Small Image URL>",
                    #     large_image_url="<Large Image URL>"
                    # )
                )
            )
        else:
            response_builder.speak(ERROR)
            response_builder.set_card(
                ui.StandardCard(
                    title="Error Sending Message",
                    text="Non 200 response from SQS",
                    # image=ui.Image(
                    #     small_image_url="<Small Image URL>",
                    #     large_image_url="<Large Image URL>"
                    # )
                )
            )
        return response_builder.response
    except ClientError as e:
        logger.error(f"Error sending SQS message: {e}")
        response_builder.speak(ERROR)
        response_builder.set_card(
            ui.StandardCard(
                title="Error Sending Message",
                text=f"ClientError: {e}",
                # image=ui.Image(
                #     small_image_url="<Small Image URL>",
                #     large_image_url="<Large Image URL>"
                # )
            )
        )
        return response_builder.response
    except ServiceException as e:
        response_builder.speak(ERROR)
        response_builder.set_card(
            ui.StandardCard(
                title="Error Sending Message",
                text=f"ServiceException: {e}",
                # image=ui.Image(
                #     small_image_url="<Small Image URL>",
                #     large_image_url="<Large Image URL>"
                # )
            )
        )
        return response_builder.response
    except Exception as e:
        raise e


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SleepIntentHandler())
sb.add_request_handler(MuteIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
