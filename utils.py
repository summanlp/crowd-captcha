from flask import request, url_for
import urllib.parse


def get_endpoint_route(endpoint):
    url_root = request.url_root
    url_endpoint = url_for(endpoint)
    return urllib.parse.urljoin(url_root, url_endpoint)