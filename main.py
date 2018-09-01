from flask import Flask, request, Response, abort, jsonify
from flask_cors import cross_origin

from question import *

app = Flask(__name__)

# TODO: not hardcode this (issue #23).
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5000",
]

@app.route('/js/crowd-captcha.js')
def js():
    """
    Takes:
      - an application uuid.

    Does:
        Process the application uuid and generates a valid js file.
        That file contains the questions (fetched from the Text
        entity) and displays a dialog from the user side.

    Returns:
      - a valid JS with questions.
    """
    if "app_uuid" not in request.args:
        abort(401)

    app_uuid = request.args["app_uuid"]
    if not Application.is_valid(app_uuid):
        abort(401)

    return get_js(app_uuid)


@app.route('/api/v1/tag', methods=["POST"])
@cross_origin(origins=ALLOWED_ORIGINS)
def tag():
    """
    Takes
      - an application uuid.
      - a user id.
      - a list of responses (text_uuid and a tag)

    Does:
        This function is called from the JS generated by the js()
        endpoint. It creates Tag entities (the answers) and also
        creates a Secret.

    Returns:
      - a secret uuid to be validated later.
    """
    data = request.get_json(force=True)
    app_uuid = data["app_uuid"]
    user_id = data["user_id"]
    tags = data["tags"]

    if not Application.is_valid(app_uuid):
        abort(401)

    if not create_tags(app_uuid, user_id, tags):
        abort(401)

    return jsonify(create_secret(app_uuid))


@app.route('/api/v1/validate', methods=["POST"])
def validate():
    """
    Takes
      - an application uuid
      - an application secret
      - a secret

    Does:
        Returns "ok" if the secret hasn't expired and is valid for the
        application and the user. Otherwise it returns "error" (400).
        Marks all the relevant tags as "validated".

    Returns:
      - whether the secret was valid or not.
    """
    data = request.get_json(force=True)
    secret = data["secret"]
    app_uuid = data["app_uuid"]
    app_secret = data["app_secret"]

    Application.auth(app_uuid, app_secret)
    if not Secret.is_valid(secret, app_uuid):
        abort(401)

    validate_captcha(secret, app_uuid)
    return jsonify({ "success": True })


@app.errorhandler(401)
def unauthorized(error):
    return Response('Contraseña, capo.', 401, {'WWWAuthenticate':'Basic realm="Login Required"'})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8181, debug=True)
