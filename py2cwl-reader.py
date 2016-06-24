from __future__ import print_function
import simplejson as json
import yaml


class CwlJson:

    def __init__(self, input_json):
        self.json = json.load(input_json)