#!/usr/bin/env python

"""
This is a short example on using the CKAN API of Avoindata.fi
This code uses the ckanapi library, see https://github.com/ckan/ckanapi
For the CKAN API in general, see http://docs.ckan.org/en/latest/api/index.html
"""

import sys
import datetime
import json
import uuid
import ckanapi


class AvoindataApiTester:

    execution_id = None
    api = None

    def __init__(self, api_base_url, api_key):
        self.execution_id = "apitest-{:%Y-%m%d-%H%M%S-%f}".format(datetime.datetime.utcnow())
        print "\nAll names in these examples are tagged with", self.execution_id

        self.api = ckanapi.RemoteCKAN(
            api_base_url,
            apikey=api_key,
            user_agent='avoindata_ckanapi_example/1.0 ({0})'.format(self.execution_id))

    def _json_print(self, data):
        print json.dumps(data, sort_keys=True, indent=2)

    def list_organizations(self):
        print "\nList all organizations (showing only 10 first here):"
        all_organizations = self.api.action.organization_list()
        self._json_print(all_organizations[:10])

    def list_datasets(self, limit=10):
        print "\nList the first {} datasets:".format(limit)
        datasets = self.api.action.package_list(limit=limit, offset=0)
        self._json_print(datasets)

    def get_organization(self, organization_id):
        print "\nGet details of organization '{}':".format(organization_id)
        organization = self.api.action.organization_show(id=organization_id)
        self._json_print(organization)

    def get_dataset(self, dataset_id):
        print "\nGet details of dataset '{}':".format(dataset_id)
        dataset = self.api.action.package_show(id=dataset_id)
        self._json_print(dataset)

    def create_test_organization(self):
        my_organization_name = 'z-org-' + self.execution_id
        print "\nCreate a new organization {}:".format(self.execution_id)
        try:
            params = {'name': my_organization_name,
                      'title': 'Z CKAN API ' + self.execution_id}
            new_organization = self.api.action.organization_create(**params)
            self._json_print(new_organization)
        except ckanapi.NotAuthorized:
            print 'Not authorized'
        return my_organization_name

    def create_test_dataset(self, owner_organization):
        print "\nCreate a new dataset:"
        my_dataset_name = 'z-' + self.execution_id
        description = 'This is a description of the dataset in the source language. Checksum: ' + str(uuid.uuid4())
        try:
            params = {'name': my_dataset_name,
                      'title': 'Z ' + self.execution_id,
                      'notes': description,
                      'license_id': 'Creative Commons Attribution 4.0',
                      'content_type': 'Paikkatieto,Avoin data,Ohjeet',
                      'collection_type': 'Open Data',
                      'owner_org': owner_organization}

            new_dataset = self.api.action.package_create(**params)
            self._json_print(new_dataset)
        except ckanapi.NotAuthorized:
            print 'Not authorized'
        return my_dataset_name

    def delete_dataset(self, dataset_id):
        print "\nDelete dataset {}:".format(dataset_id)
        self.api.action.package_delete(id=dataset_id)

    def delete_organization(self, organization_id):
        print "\nDelete organization {}:".format(organization_id)
        if organization_id != 'yksityishenkilo':
            self.api.action.organization_delete(id=organization_id)
        else:
            print "Not even trying to delete the shared organization!"

    def show_dataset_property(self, dataset_id, dataset_property):
        print "\nShow '{}' of the dataset {}:".format(dataset_property, dataset_id)
        print self.api.action.package_show(id=dataset_id).get(dataset_property)

    def show_organization_property(self, organization_id, organization_property):
        print "\nShow '{}' of the dataset {}:".format(organization_property, organization_id)
        print self.api.action.organization_show(id=organization_id).get(organization_property)


if __name__ == '__main__':

    usage = "\
    Usage: ./avoindata_ckanapi.py API_URL API_KEY\n\n\
    API_URL: URL to CKAN, excluding api directory and without trailing foreward slash\n\
             e.g. http://beta.opendata.fi/data\n\
    API_KEY: API key of the authorized user, whose permissions are used for the requests\n\
             e.g. 12345678-90ab-f000-f000-f0d9e8c7b6aa\n"

    if len(sys.argv) != 3:
        print usage
        sys.exit(1)

    apitest = AvoindataApiTester(sys.argv[1], sys.argv[2])

    apitest.list_organizations()
    apitest.get_organization('helsinki')
    apitest.list_datasets(10)
    apitest.get_dataset('valtion-budjettitalous')

    organization_name = apitest.create_test_organization()

    # You can also create your datasets to the shared 'private person'
    # Organization instead of creating your own
    # organization_name = 'yksityishenkilo'

    apitest.get_organization(organization_name)
    dataset_name = apitest.create_test_dataset(organization_name)
    apitest.get_dataset(dataset_name)

    apitest.delete_dataset(dataset_name)
    apitest.show_dataset_property(dataset_name, 'state')
    apitest.delete_organization(organization_name)
    apitest.show_organization_property(organization_name, 'state')
