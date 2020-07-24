import argparse
import csv
import json
import os

import requests
from datacite import schema43

from caltechdata_api import decustomize_schema


def get_metadata(idv):
    # Returns TCCON version of DataCite metadata

    api_url = "https://data.caltech.edu/api/record/"

    r = requests.get(api_url + str(idv)) 
    r_data = r.json()
    if "message" in r_data:
        raise AssertionError(
            "id "
            + str(idv)
            + " expected http status 200, got "
            + str(r.status_code)
            + " "
            + r_data["message"]
        )
    if not "metadata" in r_data:
        raise AssertionError("expected as metadata property in response, got " + r_data)
    metadata = r_data["metadata"]

    metadata = decustomize_schema(metadata, pass_emails=True, schema="43")
    
    try:
        assert schema43.validate(metadata)
    except AssertionError:
        v = schema43.validator.validate(metadata)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            print(error.message)
        exit()

    #Add time lag (fixed)
    metadata['release_lag'] = 30

    return metadata


#Read in site id file with CaltechDATA IDs
infile = open("site_ids.csv")
site_ids = csv.reader(infile)
ids = {}
version = {}
for row in site_ids:
    cd_idv =row[1]
    metadata = get_metadata(cd_idv)
    print(metadata)
    for idv in metadata['identifiers']:
        if idv['identifierType'] == 'id':
            tccon_id = idv['identifier']
            #Let's call this something more descriptive
            idv['identifierType'] = 'TCCON_id'
        if idv['identifierType'] == 'longName':
            longname = idv['identifier']
    outfile = open(f'metadata/{tccon_id}_{longname}.json', 'w')
    outfile.write(json.dumps(metadata))
    outfile.close()
