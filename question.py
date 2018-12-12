from flask import render_template, current_app as app
from datetime import datetime, timedelta

import statistics
from math import sqrt

import utils
import logging

from model import *
from jsmin import jsmin

import random
import yaml

with open("questions.yml", "r") as f:
    config = yaml.load(f)

NUM_QUESTIONS = config["num_questions"]
# Integrity constraint for Text.completed
MIN_QUESTIONS = config["min_questions"]
MIN_TAGS = config["min_tags"]
ERROR_THRESHOLD = config["error_threshold"]

LOGGER = logging.getLogger("crowd-captcha")

def get_questions():
    """ Returns a number of questions for the users to tag.
    """
    validation = Text.select().where(Text.completed == True).limit(1)
    discovery = Text.select().where(Text.completed == False).limit(NUM_QUESTIONS - 1)
    return validation + discovery


def create_secret(app_uuid):
    expiration = datetime.now() + timedelta(minutes=10)  # 10 mins to validate captcha.
    secret = Secret.create(application_uuid=app_uuid, expiration=expiration)
    return {
        "success": True,
        "secret": str(secret.uuid),
    }


def get_js(app_uuid):
    """ Returns the js file with the questions rendered.
    """
    slider_css = render_template("slider.css.min")
    modal = render_template("modal.html", questions=get_questions(), slider_css=slider_css)
    js = render_template("captcha.js",
                           get_endpoint_route=utils.get_endpoint_route,
                           modal=modal,
                           app_uuid=app_uuid,
                           num_questions=NUM_QUESTIONS)
    return js if app.config["DEBUG"] else jsmin(js)

def create_tags(app_uuid, user_id, tags):
    """ Creates the tags in the database.
        Returns true on success, false otherwise.
    """
    if len(tags) != NUM_QUESTIONS:
        LOGGER.error("WTF? Different tags than number of questions")
        return False

    # Apparently peewee doesn't throw an exception when you try to create
    # a record with an invalid FK, so we have to check them manually.
    for tag in tags:
        if Text.get_or_none(Text.uuid == tag["text_uuid"]) is None:
            LOGGER.error("Tag not found: " + tag["text_uuid"])
            return False

    for tag in tags:
        Tag.create(application_uuid=app_uuid,
                   user_id=user_id,
                   text_uuid=tag["text_uuid"],
                   score=tag["tag"])
        all_tags = list(Tag.select().where(Tag.text_uuid == tag["text_uuid"]))

        # I shall only consider texts tagged more than MIN_TAGS times
        # as candidates for complete texts
        # Whether they are completed depends on the error margin given by those 
        # tags
        if len(all_tags) >= MIN_TAGS:
            mean, error = mean_ci([tag.score for tag in all_tags])
            if error < ERROR_THRESHOLD:
                (Text.update(completed=True)
                    .where(Text.uuid == tag["text_uuid"])
                    .execute())
    return True

def validate_captcha(secret, app_uuid):
    """ Validates the captcha.
    """
    Secret.validate(secret)


def validate_tags(tags):
    """ Checks if the tags of already validated texts seem ok
    """
    for tag in tags:
        text = Text.get_or_none(Text.uuid == tag["text_uuid"])
        if text is None:
            return False
        if not text.completed:
            continue

        all_tags = list(Tag.select().where(Tag.text_uuid == tag["text_uuid"]))
        mean, error = mean_ci([tag.score for tag in all_tags])
        LOGGER.debug("info values {}, {}".format(mean, error))
        if not (mean - error <= float(tag["tag"]) <= mean + error):
            return False
    
    return True
