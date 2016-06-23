from __future__ import print_function
import simplejson as json
import yaml


class CwlTool:

    def __init__(self, id, author=None, version="cwl:draft-2", description=None, label=None):
        self.id = id
        self.author = author
        self.version = version
        self.description = description
        self.label = label
        self.class_ = "CommandLineTool"
        self.inputs = []
        self.outputs = []
        self.arguments = []
        self.stdout = []
        self.stdin = []
        self.baseCommand = []
        self.successCodes = []
        self.temporaryFailCodes = []
        self.hints = []
        self.add_computational_requirements()

    def add_input(self, id, type, required=True, label=None, description=None, prefix=None, cmdInclude=True, separate=True, position=None):
        new_input = {"id": id}
        new_input["label"] = label
        new_input["description"] = description
        new_input["type"] = type
        new_input["inputBinding"] = {"prefix": prefix, "sbg:cmdInclude": cmdInclude, "separate": separate, "position": position}
        if required: new_input["type"] = type
        else: new_input["type"] = str("null" + " " + type).split()
        self.inputs.append(new_input.copy())

    def add_output(self, id, type, glob, required=True, label=None, description=None):
        new_output = {"id": id}
        new_output["label"] = label
        new_output["description"] = description
        new_output["outputBinding"] = {'glob': glob}
        if required: new_output["type"] = type
        else: new_output["type"] = str("null" + " " + type).split()
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
        if aws:
            self.add_aws_instance(value=aws)

    def object2json(self):
        data = json.dumps(self, default=lambda o: clean_null_values(o.__dict__), sort_keys=True, skipkeys=True)
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

    def object2output(self, *args):
        """
        :param args is a list of output ports (CwlOutput())
        """
        for outputObject in args:
            self.outputs.append(clean_null_values(outputObject.__dict__))

class CwlInput:
    """ CWL Input Port """
    def __init__(self, id, type, required=True, label=None, description=None, prefix=None):
        self.id = id
        self.required = required
        self.label = label
        self.description = description
        if required: self.type = type
        else: self.type = str("null" + " " + type).split()
        if prefix: self.create_input_binding(prefix)

    def create_input_binding(self, prefix=None, cmdInclude=True, separate=True, position=None):
        self.inputBinding = Bindings()
        self.inputBinding.prefix = prefix
        self.inputBinding.sbg_cmdInclude = cmdInclude
        self.inputBinding.separate = separate
        self.inputBinding.position = position

class CwlOutput:
    """ CWL Output Port """
    def __init__(self, id, type, required=True, label=None, description=None, glob=None):
        self.id = id
        self.required = required
        self.label = label
        self.description = description
        self.type = type
        if glob: self.create_output_binding(glob)

    def create_output_binding(self, glob):
        self.outputBinding = Bindings()
        self.outputBinding.glob = glob

class Bindings(): pass # can use to allow sub-attributes to an attribute

def clean_null_values(input_dict):
    for k,v in input_dict.items():
        if v is None: del(input_dict[k])
        elif isinstance(v, dict): clean_null_values(v)
    return input_dict

if __name__ == "__main__":
    # input method 1
    tool = CwlTool(id="test_tool", author="gaurav")
    tool.add_base_command("python test.py")
    tool.add_docker("ubuntu:latest")
    tool.add_computational_requirements(aws="c3.xlarge")
    tool.add_argument("-t", 1, False)
    tool.add_input(id="yes", type="boolean", required=False, prefix="-r")
    tool.add_output(id="no", type="File", glob="*.txt")

    # input method 2
    tool2 = CwlTool(id="test_tool", author="gaurav")
    tool2.add_base_command("python test.py")
    tool2.add_argument(prefix="-t", separate=False)

    input2 = CwlInput(id="yes", type="boolean", required=False, prefix="-r")
    output2 = CwlOutput(id="no", type="File", glob="*.txt")

    tool2.object2input(CwlInput(id="yes", type="boolean", required=False, prefix="-r"))
    tool2.object2output(CwlOutput(id="no", type="File", glob="*.txt"))

    # print(tool2.object2yaml())
    print(tool2.object2json())
    # To run: python py2cwl.py | json_reformat | json2yaml
