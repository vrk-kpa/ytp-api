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


class AvoindataRawApiTester:

    execution_id = ""
    action_api = ""
    api_base_url = ""
    common_headers = None

    # Set this to False if you are having problems with the certificate validation
    verify_ssl = certifi.where()

    def __init__(self, api_prefix_url, api_key):
        self.execution_id = "apitest-{:%Y-%m%d-%H%M%S-%f}".format(datetime.datetime.utcnow())
        log.info("All names in these examples are tagged with {}".format(self.execution_id))

        self.api_base_url = api_prefix_url + "/api/"
        self.common_headers = {
            'authorization': api_key,
            'content-type': 'application/json',
            'user_agent': 'avoindata_ckanapi_example/1.0 ({0})'.format(self.execution_id)
        }

    def _log_response(self, response):
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

    def discover_ckan_api(self):
        """Smoke test: Tries to find a valid CKAN API from the given endpoint, and checks it for various versions."""

        latest_version = 0
        for version in range(1, 4):
            try:
                r = requests.get(self.api_base_url + str(version), verify=self.verify_ssl)
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
            sys.exit(2)
        elif latest_version != 3:
            log.warning("Found API version {0}, but version 3 is required for the next actions. Exiting")
            sys.exit(3)

        self.action_api = self.api_base_url + str(latest_version) + "/action/"
        log.debug("All API actions will be done to " + self.action_api)

    def create_test_organization(self):
        """Creates an new organization."""

        organization_name = 'z-org-' + self.execution_id
        url = self.action_api + 'organization_create'
        log.info("Trying to create organization '{0}' from '{1}'".format(organization_name, url))
        payload = {
            'name': organization_name,
            'title': 'Z CKAN API ' + organization_name
        }

        r = requests.post(url, data=json.dumps(payload), headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)
        return organization_name

    def get_organization(self, organization_name):
        """Retrieves organization"""

        url = self.action_api + 'organization_show'
        log.info("Trying to get organization '{0}' from '{1}'".format(organization_name, url))
        payload = {
            'id': organization_name
        }

        # For some reason, this call fails if done as a GET call with URL params. POST can be used here.
        r = requests.post(url, data=json.dumps(payload), headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)

    def delete_organization(self, organization_name):
        """Removes organization"""

        url = self.action_api + 'organization_delete'
        log.info("Trying to delete organization '{0}' from '{1}'".format(organization_name, url))
        payload = {
            'id': organization_name,
        }

        r = requests.post(url, data=json.dumps(payload), headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)

    def create_test_dataset(self, organization_name):
        """Create a dataset"""

        dataset_name = 'z-' + self.execution_id
        url = self.action_api + 'package_create'
        log.info("Trying to create dataset '{0}' from '{1}'".format(dataset_name, url))
        payload = {
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

        r = requests.post(url, data=json.dumps(payload), headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)
        return dataset_name

    def get_dataset(self, dataset_name):
        """Retrieves dataset"""

        url = self.action_api + 'package_show'
        log.info("Trying to get package '{0}' from '{1}'".format(dataset_name, url))
        params = {
            'id': dataset_name
        }

        r = requests.get(url, params=params, headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)

    def delete_dataset(self, dataset_name):
        """Removes dataset"""

        url = self.action_api + 'package_delete'
        log.info("Trying to delete dataset '{0}' from '{1}'".format(dataset_name, url))
        payload = {
            'id': dataset_name,
        }

        r = requests.post(url, data=json.dumps(payload), headers=self.common_headers, verify=self.verify_ssl)
        self._log_response(r)


if __name__ == '__main__':

    usage = "\
    Usage: ./avoindata_rawhttp.py API_URL API_KEY\n\n\
    API_URL: URL to CKAN, excluding api directory and without trailing foreward slash\n\
             e.g. http://beta.opendata.fi/data\n\
    API_KEY: API key of the authorized user, whose permissions are used for the requests\n\
             e.g. 12345678-90ab-f000-f000-f0d9e8c7b6aa\n"

    if len(sys.argv) != 3:
        print usage
        sys.exit(1)

    apitest = AvoindataRawApiTester(sys.argv[1], sys.argv[2])
    apitest.discover_ckan_api()

    organization_name = apitest.create_test_organization()

    # You can also create your datasets to the shared 'private person'
    # Organization instead of creating your own
    # organization_name = 'yksityishenkilo'

    apitest.get_organization(organization_name)
    dataset_name = apitest.create_test_dataset(organization_name)
    apitest.get_dataset(dataset_name)

    apitest.delete_dataset(dataset_name)
    apitest.delete_organization(organization_name)
