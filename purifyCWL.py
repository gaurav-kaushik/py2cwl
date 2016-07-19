from __future__ import print_function
import argparse
import json
from py2cwlreader import CwlReader
from py2cwlwriter import clean_null_values


def purify(input_dict):
    """
    :param input_dict: input JSON file
    This will do some checks to purify a CWL JSON file pulled from the platform.
    Now you can easily share externally (e.g. on GitHub) or add to other projects without links.
    Note the following:
    - custom fields inside ports are not scrubbed so IO behavior is maintained (may be tool-critical)
    - for workflows, "sbg:id" cannot be deleted or be empty, so we set it and "id" to "-"
    """
    app = input_dict

    # 1. Empty the id
    app["id"] = "-"

    # 2. Remove any sbg-specific fields not in the whitelist. This is enough for tools.
    field_whitelist = ["sbg:categories", "sbg:id", "sbg:toolAuthor", "sbg:toolkit", "sbg:id"]
    for k in app.keys():
        if k.startswith("sbg:") and k not in field_whitelist: app.pop(k)

    # 3. For workflows, recursively purify apps in the "run" key of the "steps" key
    for s in app.get('steps', []):
        if 'run' in s: s['run'] = purify(s['run'])

    return app

def object2json(input_app):
    """
    :param input_app: takes an app object and converts to JSON
    """
    app = json.dumps(input_app, default=lambda o: clean_null_values(o.__dict__), sort_keys=True,
                     skipkeys=True, indent=2)
    app = app.replace("class_", "class")
    return app

def save_app(app, output_filename=None):
    if output_filename:
        args_file = output_filename + ".cwl"
        with open(args_file, "w") as output:
            print(object2json(app), file=output)
        print("Purified file saved at: " + args_file)
    else:
        print(object2json(app))


if __name__ == "__main__":
    # parse those args
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", default=None, help="Specify path to CWL file")
    parser.add_argument("-o", "--output", default=None, help="Redirect to an output file (ext: .cwl)")
    args = parser.parse_args()
    args_json = args.json
    args_output = args.output

    # purify the CWL application
    input_json = CwlReader(in_json=args_json)
    app_dict = input_json.Tool.__dict__
    save_app(purify(app_dict), args_output)

    # Usage: python purifyCWL.py -j <input.json> -o <output_filename>
