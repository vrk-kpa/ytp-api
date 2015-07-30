#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a short example on using the CKAN API of Avoindata.fi
For the CKAN API in general, see http://docs.ckan.org/en/latest/api/index.html
The older docs http://docs.ckan.org/en/ckan-1.7.1/api.html#tools-for-accessing-the-api
also list some tools and libs for accessing the API.
"""

import logging
import datetime
import requests
import certifi
import json
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set this to False if you are having problems with the certificate validation
verify_ssl = certifi.where()


def look_for_ckan_api(base_url):
    """Smoke test: Tries to find a valid CKAN API from the given endpoint, and checks it for various versions."""

    latest_version = 0

    for version in range(1, 4):
        try:
            r = requests.get(base_url + str(version), verify=verify_ssl)
            try:
                if json.dumps(r.json()) == '{{"version": {0}}}'.format(version):
                    log.debug("API version {0} found".format(version))
                    latest_version = version
            except ValueError:
                log.warning("Could not parse JSON from the given address")
        except requests.ConnectionError as e:
            log.error(e)
            log.error("Could not connect to given url")

    if latest_version == 0:
        log.error("Could not find a valid API from the given URL")
        sys.exit(1)
    elif latest_version != 3:
        log.warning("Found API version {0}, but version 3 is required for the next actions. Exiting")
        sys.exit(2)

    return base_url + str(latest_version) + "/action/"


def create_organization(organization_name, api_url, api_key):
    """Creates an new organization."""

    request_url = api_url + 'organization_create'
    log.info("Trying to create organization '{0}' from '{1}'".format(organization_name, request_url))
    request_payload = {
        'name': organization_name,
        'title': 'Z CKAN API ' + organization_name
    }
    request_headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    r = requests.post(request_url, data=json.dumps(request_payload), headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def get_organization(organization_name, api_url, api_key):
    """Retrieves organization"""

    request_url = api_url + 'organization_show'
    log.info("Trying to get organization '{0}' from '{1}'".format(organization_name, request_url))
    request_payload = {
        'id': organization_name
    }
    request_headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    r = requests.get(request_url, params=request_payload, headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def delete_organization(organization_name, api_url, api_key):
    """Removes organization"""

    request_url = api_url + 'organization_delete'
    log.info("Trying to delete organization '{0}' from '{1}'".format(organization_name, request_url))
    request_payload = {
        'id': organization_name,
    }
    request_headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    r = requests.post(request_url, data=json.dumps(request_payload), headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def create_dataset(dataset_name, organization_name, api_url, api_key):
    """Create a dataset"""

    request_url = api_url + 'package_create'
    log.info("Trying to create dataset '{0}' from '{1}'".format(dataset_name, request_url))
    request_payload = {
        'name': dataset_name,
        'title': 'Z ' + dataset_name,
        'owner_org': organization_name,
        'notes': 'A temporary test dataset that can be deleted at any possible time',
        'collection_type': 'Open Data',
        'content_type': 'paikkatieto, mallintaminen',
        'license_id': 'cc-by-4.0',
        'tag_string': 'foo, bar',
        'extras': [
            {'key': 'firstkey', 'value': 'firstvalue'},
            {'key': 'secondkey', 'value': 'secondvalue'},
            {'key': 'thirdkey', 'value': 'thirdvalue'}
            ]
    }
    request_headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    r = requests.post(request_url, data=json.dumps(request_payload), headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def get_dataset(dataset_name, api_url, api_key):
    """Retrieves dataset"""

    request_url = api_url + 'package_show'
    log.info("Trying to get package '{0}' from '{1}'".format(dataset_name, request_url))
    request_payload = {
        'id': dataset_name
    }
    request_headers = {
        'authorization': api_key
    }

    r = requests.get(request_url, params=request_payload, headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def delete_dataset(dataset_name, api_url, api_key):
    """Removes dataset"""

    request_url = api_url + 'package_delete'
    log.info("Trying to delete dataset '{0}' from '{1}'".format(dataset_name, request_url))
    request_payload = {
        'id': dataset_name,
    }
    request_headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    r = requests.post(request_url, data=json.dumps(request_payload), headers=request_headers, verify=verify_ssl)
    log_response(r)

    return


def log_response(response):
    """Try to print the response in JSON or fallback to text"""

    if response.status_code == 200:
        log.debug(json.dumps(response.json(), indent=2, sort_keys=True))
        if response.json()['success']:
            log.info("Success")
    elif response.status_code == 500:
        log.error("Server error (status 500)")
    else:
        log.warning("Status code: %s" % response.status_code)
        try:
            log.warning(json.dumps(response.json(), indent=2, sort_keys=True))
        except ValueError:
            log.warning("Not valid JSON: %s\n" % response.text)
    return


if __name__ == '__main__':

    usage = "\
    Usage: ./avoindata_rawhttp.py API_URL API_KEY\n\n\
    API_URL: URL to CKAN, excluding api directory and without trailing foreward slash\n\
             e.g. http://beta.opendata.fi/data\n\
    API_KEY: API key of the authorized user, whose permissions are used for the requests\n\
             e.g. 12345678-90ab-f000-f000-f0d9e8c7b6aa\n"

    if len(sys.argv) != 3:
        print usage
        sys.exit(3)

    url_prefix = sys.argv[1] + "/api/"
    api_key = sys.argv[2]
    api_url = look_for_ckan_api(url_prefix)

    log.info("Now using API URL " + api_url)

    execution_id = "apitest-{:%Y-%m%d-%H%M%S-%f}".format(datetime.datetime.utcnow())
    organization_name = "z-org-" + execution_id
    dataset_name = "z-" + execution_id

    create_organization(organization_name, api_url, api_key)
    get_organization(organization_name, api_url, api_key)
    create_dataset(dataset_name, organization_name, api_url, api_key)
    get_dataset(dataset_name, api_url, api_key)
    delete_dataset(dataset_name, api_url, api_key)
    delete_organization(organization_name, api_url, api_key)
