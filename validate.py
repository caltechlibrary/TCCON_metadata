import json
from datacite.schema43 import validate, validator

infile = 'park_falls.json'

metaf = open(infile, 'r')
metadata = json.load(metaf)

valid = validate(metadata)
# Debugging if verification fails
if valid == False:
    v = validator.validate(metadata)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        print(error.message)


