# IMPORTING THE NECCESSARY PACKAGES

import json

# The parse FUNCTION

def parse(Payload: any) -> dict:

    TextConvert = json.dumps(Payload, indent=4)
    ParsedToDict = json.loads(TextConvert)

    return ParsedToDict
