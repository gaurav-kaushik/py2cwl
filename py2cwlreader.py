from __future__ import print_function
import argparse
import simplejson as json
import yaml
from py2cwlwriter import CwlTool

class Tool:
    def __init__(self, **fields):
        self.__dict__.update(fields)

class CwlReader:

    def __init__(self, in_json=False, in_yaml=False):
        if in_json:
            self.Json = Json()
            try:
                with open(in_json, 'r') as j:
                    self.Json = json.load(j) # import from file
            except:
                self.Json = json.loads(in_json) # import from json string
            self.Tool = Tool(**self.Json)

        elif in_yaml:
            self.Yaml = Yaml()
            with open(in_yaml, 'r') as y:
                self.Yaml = yaml.safe_load(y) # import from files
            self.Tool = Tool(**self.Yaml)
        else:
            print("Please input JSON or YAML")


class Json(): pass
class Yaml(): pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", default=None)
    parser.add_argument("-y", "--yaml", default=None)
    args = vars(parser.parse_args())

    ## instantiate json file
    tool = CwlReader(in_json=args['json'], in_yaml=args['yaml'])
    # instantiate with json string
    # tool = CwlReader('{"Hello":"World", "inputs":[{"id":"yes"}]}')

    # Tests
    # try: print(tool.Json)
    # except: print("No Json")
    #
    # try: print(yaml.dump(tool.Yaml))
    # except: print("No Yaml")
    #
    # try: print(tool.Tool.__dict__)
    # except: print("No Tool")

    # try: print(vars(tool.Tool))
    # except: print("No Tool")

    c = CwlTool(id="datboi", label="ohshitwaddup")
    print(vars(c))