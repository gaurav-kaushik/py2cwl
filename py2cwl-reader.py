from __future__ import print_function
import simplejson as json
# import yaml
import argparse

class CwlReader:

    def __init__(self, in_json=False, in_yaml=False):
        if in_json:
            # Check for input as JSON
            try:
                # import from file
                with open(in_json, 'r') as j:
                    self.Json = json.load(j)
            except:
                # import from json string
                self.Json = json.loads(in_json)

        if in_yaml:
            # more to come
            return

    def json2yaml(self):
        """
        Convert CwlReader.Json to Yaml format and clean up
        """
        return

    def yaml2json(self):
        """
        Convert CwlReader.Json to Yaml format and clean up
        """
        return

class Json(): pass
class Yaml(): pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", default=None)
    parser.add_argument("-y", "--yaml", default=None)
    args = vars(parser.parse_args())

    # instantiate json file
    tool = CwlReader(in_json=args['json'], in_yaml=args['yaml'])

    # instantiate with json string
    # tool = CwlReader('{"Hello":"World"}')

    # Tests
    print(tool.Json)
    print(tool.__dict__)
    try:
        print(tool.Json['inputs'])
    except:
        print("No such key")
