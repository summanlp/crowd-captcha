from peewee import *
from uuid import uuid4
from datetime import datetime
import yaml
import os
import hashlib
import secrets

dir_path = os.path.dirname(os.path.realpath(__file__))
db_yml = os.path.join(dir_path, "db.yml")
db_config = yaml.load(open(db_yml))
db = PostgresqlDatabase(db_config["database"], user=db_config["user"], password=db_config["password"])   # TODO: change to mysql.

# Development db.
#db = SqliteDatabase('crowd_captcha.db')


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
    secret_hash = CharField()
    salt = CharField()

    @classmethod
    def make_hash(Application, secret, salt):
        sha256 = hashlib.sha256()
        sha256.update(secret.encode())
        sha256.update(salt.encode())
        return sha256.hexdigest()

    @classmethod
    def create(Application, uuid, name, secret):
        # "A good rule is of thumb is to use a salt that is the same size as
        # the output of the hash function." (crackstation.net)
        salt = secrets.token_hex(32)
        secret_hash = Application.make_hash(secret, salt)

        return super().create(uuid=uuid, name=name, secret_hash=secret_hash, salt=salt)

    @classmethod
    def auth(Application, uuid, secret):
        app = Application.get_or_none(uuid)

        if app is None:
            return False

        return app.secret_hash == Application.make_hash(secret, app.salt)

    @classmethod
    def is_valid(Application, uuid):
        return (Application
                    .select()
                    .where(Application.uuid == uuid)
                    .count() == 1)


class Text(DatabaseModel):
    """ This entity stores the texts to be served to the users.

    uuid: the id of the text.
    text: the text.
    source: the source from where the text was retrieved (for instance,
      the twitter url.
    created: the date when it was created.    
    completed: whether the text has sufficient ratings or needs to be served
    """

    uuid = UUIDField(default=uuid4, primary_key=True)
    text = TextField()
    source = CharField()
    created = DateTimeField(default=datetime.now)
    completed = BooleanField(default=False)


class Tag(DatabaseModel):
    """ These are the instances of the user submitted tags.

    uuid: the id of the tag.
    application_uuid: the uuid of the application that showed the user
      a given text.
    text_uuid: the uuid of the text.
    user_id: an identifier to map whose submittion it was.
    score: a polarity score
    timestamp: the date this was submitted.
    validated: holds whether the form was submitted after the tag was
      recorded.
    """
    uuid = UUIDField(default=uuid4, primary_key=True)
    application_uuid = ForeignKeyField(Application)
    text_uuid = ForeignKeyField(Text)
    user_id = CharField()
    score = DoubleField()
    created = DateTimeField(default=datetime.now)
    validated = BooleanField(default=False)

    # TODO: add foreign keys for secret_uuid (issue #12).


class Secret(DatabaseModel):
    """ This stores the secrets given to users to pass the captcha.

    uuid: the uuid of the secret.
    application_uuid: the uuid of the application.
    expiration: the expiration date of the secret.
    validated: holds whether the form was submitted after the tag was
      recorded.

    """
    uuid = UUIDField(default=uuid4, primary_key=True)
    application_uuid = UUIDField()
    expiration = DateTimeField()
    validated = BooleanField(default=False)

    @classmethod
    def is_valid(Secret, secret, app_uuid):
        return (Secret
                .select()
                .where(Secret.uuid == secret &
                       Secret.application_uuid == app_uuid &
                       Secret.expiration <= datetime.now() &
                       Secret.validated == False)
                .count() > 0)

    @classmethod
    def validate(Secret, secret):
        (Secret
            .update({ Secret.validated: True })
            .where(Secret.uuid == secret)
            .execute())

    # TODO: add foreign keys for application_uuid and text_uuid (issue #12).


def create_tables():
    with db:
        db.create_tables([Application, Text, Tag, Secret])
