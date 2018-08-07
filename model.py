from peewee import *
from uuid import uuid4


db = SqliteDatabase('captcha.db')   # TODO: change to mysql.


class DatabaseModel(Model):
    class Meta:
        database = db


class Application(DatabaseModel):
    """ This represents the applications that use the system.
    An application can't make requests to the app unless it's
    registered.
    
    uuid: the id of the application.
    name: the common, human readable name of the application.
    secret: the password that the application will use to validate the
      requests.
    """

    uuid = UUIDField(default=uuid4, primary_key=True)
    name = CharField()
    secret = CharField()


class Text(DatabaseModel):
    """ This entity stores the texts to be served to the users.
    
    uuid: the id of the text.
    text: the text.
    source: the source from where the text was retrieved (for instance,
      the twitter url.
    created: the date when it was created.    
    """

    uuid = UUIDField(default=uuid4, primary_key=True)
    text = TextField()
    source = CharField()
    created = DateField()

  
class Tag(DatabaseModel):
    """ These are the instances of the user submitted tags.
    
    uuid: the id of the tag.
    application_uuid: the uuid of the application that showed the user
      a given text.
    text_uuid: the uuid of the text.
    user_id: an identifier to map whose submittion it was.
    tag: a string with the tag.
    secret_uuid: the uuid of the secret.
    timestamp: the date this was submitted.
    validated: holds whether the form was submitted after the tag was
      recorded.
    """
    uuid = UUIDField(default=uuid4, primary_key=True)
    application_uuid = UUIDField()
    text_uuid = UUIDField()
    user_id = CharField()
    tag = CharField()
    secret_uuid = UUIDField()
    created = DateField()
    validated = BooleanField()
    
    # TODO: add foreign keys for application_uuid, text_uuid, and
    #       secret_uuid.


class Secret(DatabaseModel):
    """ This stores the secrets given to users to pass the captcha.
    
    uuid: the uuid of the secret.
    text_uuid: the uuid of the text.
    user_id: an identifier to map whose submittion it was.
    expiration: the expiration date of the secret.
    validated: holds whether the form was submitted after the tag was
      recorded.
    
    """
    uuid = UUIDField(default=uuid4, primary_key=True)
    application_uuid = UUIDField()
    text_uuid = UUIDField()
    user_id = CharField()
    valid_until = DateField()
    validated = BooleanField()
    
    # TODO: add foreign keys for application_uuid and text_uuid.
