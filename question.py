from datetime import datetime, timedelta
from model import *

def get_questions():
    """ Returns a number of questions for the users to tag.
    """
    # TODO: implement me.
    return Text.select()


def create_secret(app_uuid):
    expiration = datetime.now + timedelta(minutes=10)  # 10 mins to validate captcha.
    secret = Secret.create(application_uuid=app_uuid, expiration=expiration)
    return secret.uuid


def get_js(app_uuid):
    """ Returns the js file with the questions rendered.
    """
    questions = get_questions()
    # TODO: implement actual js.
    return "\n".join(text.uuid " - " + text.text for tex in questions)


def create_tags(app_uuid, user_id, tags):
    """ Creates the tags in the database.
    """
    for tag in tags:
        Tag.create(application_uuid=app_uuid,
                   text_uuid=tag["text_uuid"],
                   user_id=tag["user_id"],
                   tag=tag["tag"])


def validate_captcha():
    """ Validates the captcha.
    """
    if not Secret.is_valid(secret, app_uuid):
        raise Exception()  # TODO: throw 404.

    Secret.validate(secret)
