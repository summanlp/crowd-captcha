from flask import request, url_for
import urllib.parse
import numpy as np
import scipy


def get_endpoint_route(endpoint):
    url_root = request.url_root
    url_endpoint = url_for(endpoint)
    return urllib.parse.urljoin(url_root, url_endpoint)


def mean_ci(sample, confidence=0.95):
    a = np.array(sample).astype(np.float64)
    n = a.size
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, h
