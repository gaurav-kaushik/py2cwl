from __future__ import print_function
import json
import yaml


class CwlTool:

    def __init__(self, id, label, author=None, version="cwl:draft-2", description=None):
        # required descriptive fields
        self.id = id
        self.author = author
        self.version = version
        self.description = description
        self.label = label
        self.class_ = "CommandLineTool"
        # IO/args
        self.inputs = []
        self.outputs = []
        self.arguments = []
        # stdin/out
        self.stdout = ""
        self.stdin = ""
        # base command
        self.baseCommand = []

        # misc
        self.successCodes = []
        self.temporaryFailCodes = []
        self.hints = []
        self.add_computational_requirements()

    def add_input(self, id, type, required=True, label=None, description=None,
                        prefix=None, cmdInclude=True, separate=True, position=None):
        new_input = {"id": id}
        new_input["label"] = label
        new_input["description"] = description
        new_input["type"] = type
        new_input["inputBinding"] = {"prefix": prefix, "sbg:cmdInclude": cmdInclude,
                                     "separate": separate, "position": position}
        if not required: new_input["type"] = ["null"]
        else: new_input["type"] = ["null", str(type)]
        self.inputs.append(new_input.copy())

    def add_output(self, id, type, glob, required=True, label=None, description=None):
        new_output = {"id": id}
        new_output["label"] = label
        new_output["description"] = description
        new_output["outputBinding"] = {'glob': glob}
        if not required: new_output["type"] = ["null"]
        else: new_output["type"] = ["null", str(type)]
        self.outputs.append(new_output.copy())

    def add_argument(self, prefix=None, order=None, separate=True):
        new_argument = {"prefix": prefix, "order": order, "separate": separate}
        self.arguments.append(clean_null_values(new_argument.copy()))

    def add_base_command(self, base=None):
        self.baseCommand = base.split()

    def add_docker(self, dockerPull, dockerImageID=None):
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
        if aws: self.add_aws_instance(value=aws)

    def object2json(self):
        """
        methods to clean up the object when converting to JSON
        """
        data = json.dumps(self, default=lambda o: clean_null_values(o.__dict__),
                                sort_keys=True, skipkeys=True, indent=2)
        data = data.replace("class_", "class")
        data = data.replace("sbg_cmdInclude", "sbg:cmdInclude")
        return data

    def object2yaml(self):
        return yaml.safe_dump(self.object2json())

    def object2input(self, *args):
        """
        :param args is a list of input ports (CwlInput())
        """
        for inputObject in args:
            self.inputs.append(clean_null_values(inputObject.__dict__))

    def object2argument(self, *args):
        """
        :param args is a list of arguments (CwlArgument())
        """
        for argObject in args:
            self.arguments.append(clean_null_values(argObject.__dict__))

    def object2output(self, *args):
        """
        :param args is a list of output ports (CwlOutput())
        """
        for outputObject in args:
            self.outputs.append(clean_null_values(outputObject.__dict__))

class CwlInput:
    """ CWL Input Port """
    def __init__(self, id, type, required=True, label=None, description=None, prefix=None, separate=True, position=0):
        self.id = check_id_hash(id)
        if required: self.type = [str(type)] # will change this later to handle arrays
        else: self.type = ["null", str(type)]
        self.required = required
        self.label = label
        self.description = description
        if prefix: self.create_input_binding(prefix, separate, position)

    def create_input_binding(self, prefix, separate, position, cmdInclude=True):
        self.inputBinding = Bindings()
        self.inputBinding.prefix = prefix
        self.inputBinding.separate = separate
        self.inputBinding.position = position
        self.inputBinding.sbg_cmdInclude = cmdInclude # include by default, later can inject javascript expression

class CwlOutput:
    """ CWL Output Port """
    def __init__(self, id, type, glob, required=True, label=None, description=None):
        self.id = check_id_hash(id)
        if required: self.type = [str(type)] # will change this later to handle arrays
        else: self.type = ["null", str(type)]
        self.create_output_binding(glob)
        self.required = required
        self.label = label
        self.description = description

    def create_output_binding(self, glob):
        self.outputBinding = Bindings()
        self.outputBinding.glob = glob

class CwlArgument:
    """ CWL Arguments """
    def __init__(self, valueFrom, prefix=None, separate=False, position=0):
        self.valueFrom = valueFrom
        self.prefix = prefix
        self.separate = separate
        self.position = position

class Bindings(): pass # can use to allow sub-attributes to an attribute

def clean_null_values(input_dict):
    for k,v in input_dict.items():
        if v is None: del(input_dict[k])
        elif isinstance(v, dict): clean_null_values(v)
    return input_dict

def check_id_hash(id):
    if id.startswith('#'):
        return id
    else:
        return '#' + id

if __name__ == "__main__":

    # create cwl tool
    tool = CwlTool(id="test_tool", author="gaurav", label="testing123")
    tool.add_base_command("python test.py")
    tool.add_docker(dockerPull="ubuntu:latest")

    # add input ports
    input1 = CwlInput(id="yes", type="boolean", required=False, prefix="-y")
    input2 = CwlInput(id="maybe", type="File", prefix="-m")
    tool.object2input(input1)
    tool.object2input(input2)

    # add arguments
    argument1 = CwlArgument(prefix="-r", valueFrom=30, separate=True, position=1)
    argument2 = CwlArgument(valueFrom="--verbose", position=99)
    tool.object2argument(argument1)
    tool.object2argument(argument2)

    # add output ports
    tool.object2output(CwlOutput(id="no", type="File", glob="*.txt"))

    # pretty print to console
    print(tool.object2json())

    # To run: python py2cwl.py | json2yaml