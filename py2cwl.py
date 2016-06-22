from __future__ import print_function
from subprocess import call
import json
import yaml


class CwlTool:

    def __init__(self, id="", author="", version="cwl:draft-2", description="", label=""):
        self.id = id
        self.author = author
        self.version = version
        self.description = description
        self.label = label
        self.app_class = "CommandLineTool"
        self.inputs = []
        self.outputs = []
        self.arguments = []
        self.stdout = []
        self.stdin = []
        self.baseCommand = []
        self.successCodes = []
        self.temporaryFailCodes = []
        self.hints = []
        return

    def add_input(self, id, required=True, label="", description="", type="File", prefix="", cmdInclude=True, separate=True, position=0):
        new_input = {"id": id}
        new_input["label"] = label
        new_input["description"] = description
        new_input["type"] = type
        new_input["inputBinding"] = {"prefix": prefix, "sbg:cmdInclude": cmdInclude, "separate": str(separate).lower(), "position": position}
        if required:
            new_input["type"] = type
        else:
            new_input["type"] = str("null" + " " + type).split()
        self.inputs.append(new_input.copy())

    def add_output(self, id, required=True, label="", description="", type="File", glob=""):
        new_output = {"id": id}
        new_output["label"] = label
        new_output["description"] = description
        new_output["outputBinding"] = {'glob': glob}
        if required:
            new_output["type"] = type
        else:
            new_output["type"] = str("null" + " " + type).split()
        self.outputs.append(new_output.copy())

    def add_argument(self, prefix="", order=0, separate=True):
        new_argument = {"prefix": prefix, "order": order, "separate": str(separate).lower()}
        self.arguments.append(new_argument.copy())

    def add_base_command(self, base=""):
        self.baseCommand = base.split()

    def add_docker(self, dockerPull="", dockerImageID=""):
        docker = {"class": "DockerRequirement", "dockerPull": dockerPull, "dockerImageID": dockerImageID}
        self.hints.append(docker.copy())

    def add_cpu(self, value):
        cpu = {"class": "sbg:CPURequirement", "value": value}
        self.hints.append(cpu.copy())

    def add_mem(self, value):
        mem = {"class": "sbg:MemRequirement", "value": value}
        mem["value"] = value
        self.hints.append(mem.copy())

    def add_aws_instance(self, value):
        aws = {"class": "sbg:AWSInstanceType", "value": value}
        self.hints.append(aws.copy())

    def add_computational_requirements(self, cpu=1, mem=1000, aws=None):
        self.add_cpu(value=cpu)
        self.add_mem(value=mem)
        if aws:
            self.add_aws_instance(value=aws)

    def object2json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    # def pretty_print_json(self):
    #     print(json.dumps(self.object2json(), sort_keys=True, indent=4, separators=(',', ': ')))

class CwlInput:

    def __init__(self, id, required=True, label="", description="", type="File", prefix="", cmdInclude=True, separate=True, position=0):
        self.id = id
        self.required = required
        self.label = label
        self.description = description
        if required:
            self.type = type
        else:
            self.type = str("null" + " " + type).split()

    def create_input_binding(self, prefix="", cmdInclude=True, separate=True, position=0):
        self.inputBinding = Bindings()
        self.inputBinding.prefix = prefix
        self.inputBinding.sbg_cmdInclude = cmdInclude
        self.inputBinding.separate = separate
        self.inputBinding.position = position


class CwlOutput:

    def __init__(self, id, required=True, label="", description="", type="File", glob=""):
        self.id = id
        self.required = required
        self.label = label
        self.description = description
        self.type = str(type)

    def create_output_binding(self, prefix="", cmdInclude=True, separate=True, position=0, glob=""):
        self.outputBinding = Bindings()
        self.outputBinding.prefix = prefix
        self.outputBinding.sbg_cmdInclude = cmdInclude
        self.outputBinding.separate = separate
        self.outputBinding.position = position
        self.outputBinding.glob = glob

class Bindings(): pass # can use to allow sub-attributes to an attribute

if __name__ == "__main__":
    tool = CwlTool()
    tool.add_input(id="yes", type="boolean")
    tool.add_base_command("python test.py")
    tool.add_docker("ubuntu:latest")
    tool.add_computational_requirements(aws="c3.xlarge")
    tool.add_argument("-t", 1, False)

    print(tool.object2json())
    # To run: python py2cwl.py | json_reformat

