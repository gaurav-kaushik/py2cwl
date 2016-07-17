from __future__ import print_function
import argparse
import json
from py2cwlreader import CwlReader
from py2cwlwriter import clean_null_values

def purify(input_dict):
    """
    :param file: input JSON file
    This will do some checks to purify a CWL JSON file pulled from the platform.
    Now you can easily share externally (e.g. on GitHub) or add to other projects without links.
    """
    tool = input_dict
    for k in tool.keys():
        if k.startswith("sbg:"):
            tool.pop(k)
    tool["id"] = ""
    return tool

def object2json(input_tool):
    """ methods to clean up the object when converting to JSON """
    data = json.dumps(input_tool, default=lambda o: clean_null_values(o.__dict__),
                            sort_keys=True, skipkeys=True, indent=2)
    data = data.replace("class_", "class")
    return data


if __name__ == "__main__":
    # parse those args
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", default=None, help="Specify path to CWL file")
    parser.add_argument("-o", "--output", default=None, help="Redirect to an output file (ext: .cwl)") # choose whether to save
    args = parser.parse_args()
    args_json = args.json

    # purify the tool
    tool = CwlReader(in_json=args_json)
    tool_dict = tool.Tool.__dict__
    purified_tool = purify(tool_dict)

    # save if desired or print to console
    if args.output:
        args_file = args.output + ".cwl"
        with open(args_file, "w") as output:
            print(object2json(purified_tool), file=output)
        print("Purified file saved at: " + args_file)
    else:
        print(object2json(purified_tool))
