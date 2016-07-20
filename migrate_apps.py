from __future__ import print_function
import argparse
import sbgapitools

if __name__ == "__main__":
    # parse those args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_project", nargs="+", help="Project you're pulling apps from")
    parser.add_argument("-o", "--output_project", default=None, help="Project you're pushing to")
    args = parser.parse_args()
    args_in = args.input_project
    args_out = args.output_project
    sbgapitools.transfer_clean_apps(args_in, args_out)

