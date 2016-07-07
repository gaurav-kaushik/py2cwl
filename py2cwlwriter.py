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
        self.requirements = [] # double-check that this can be imported as an empty list and doesn't need to be ""
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
        # consider changing input type to list of strings to make it easier to check for expressions

    def add_docker(self, dockerPull, dockerImageID=None):
        docker = {"class": "DockerRequirement", "dockerPull": dockerPull, "dockerImageID": dockerImageID}
        self.hints.append(docker.copy())

    def add_cpu(self, value):
        cpu = {"class": "sbg:CPURequirement", "value": self.tool_expression_check(value)}
        self.hints.append(cpu.copy())

    def add_mem(self, value):
        mem = {"class": "sbg:MemRequirement", "value": self.tool_expression_check(value)}
        self.hints.append(mem.copy())

    def add_aws_instance(self, value):
        aws = {"class": "sbg:AWSInstanceType", "value": value}
        self.hints.append(aws.copy())

    def add_computational_requirements(self, cpu=1, mem=1000, aws=None):
        self.add_cpu(cpu)
        self.add_mem(mem)
        if aws: self.add_aws_instance(aws)

    def add_stdin(self, stdin):
        self.stdin = self.tool_expression_check(stdin)

    def add_stdout(self, stdout):
        self.stdout = self.tool_expression_check(stdout)

    def tool_expression_check(self, value):
        # ensure that the appropriate requirements for having expressions exists
        self.requirements_check()
        return expression_check(value)

    def requirements_check(self):
        if not any(d["class"] == "ExpressionEngineRequirement" for d in self.requirements):
            expr_reqs = dict()
            expr_reqs["class"] = "ExpressionEngineRequirement"
            expr_reqs["id"] = "#cwl-js-engine"
            expr_reqs["requirements"] = [{"class": "DockerRequirement", "dockerPull": "rabix/js-engine"}]
            self.requirements.append(expr_reqs)

    def object2json(self):
        """ methods to clean up the object when converting to JSON """
        data = json.dumps(self, default=lambda o: clean_null_values(o.__dict__),
                                sort_keys=True, skipkeys=True, indent=2)
        data = data.replace("class_", "class")
        data = data.replace("sbg_cmdInclude", "sbg:cmdInclude") # consider generalizing to sbg_ -> sbg:
        return data

    def object2yaml(self):
        return yaml.safe_dump(self.object2json())

    def object2input(self, *args):
        """ param args is a list of input ports (CwlInput()) """
        for inputObject in args:
            self.inputs.append(clean_null_values(inputObject.__dict__))
        # Add checker for dynamic expressions in input objects -> self.requirements.check

    def object2argument(self, *args):
        """ param args is a list of arguments (CwlArgument()) """
        for argObject in args:
            self.arguments.append(clean_null_values(argObject.__dict__))

    def object2output(self, *args):
        """ param args is a list of output ports (CwlOutput()) """
        for outputObject in args:
            self.outputs.append(clean_null_values(outputObject.__dict__))

class CwlInput:
    """ CWL Input Port """
    def __init__(self, id, type, items=None, symbols=None, required=True,
                       label=None, description=None, prefix=None,
                       separate=True, position=0, valueFrom=None, secondaryFiles=[]):
        self.id = check_id_hash(id)
        self.type = [type_parser(type, id, items, symbols)]
        if not required: self.type.insert(0, "null")
        self.label = label
        self.description = description
        if prefix: self.create_input_binding(prefix, separate, position, secondaryFiles)
        if valueFrom: self.valueFrom = expression_check(valueFrom)

    def create_input_binding(self, prefix, separate, position, secondaryFiles, cmdInclude=True):
        self.inputBinding = Bindings()
        self.inputBinding.prefix = prefix
        self.inputBinding.separate = separate
        self.inputBinding.position = position
        if not isinstance(secondaryFiles, list): secondaryFiles = [secondaryFiles]
        self.inputBinding.secondaryFiles = [expression_check(value) for value in secondaryFiles]
        self.inputBinding.sbg_cmdInclude = cmdInclude # include by default, later can inject javascript expression

class CwlOutput:
    """
    CWL Output Port
    required fields: id, type, glob
    to glob an array, set type=array and give the "items" (e.g. type="array", items="File" for array of files)
    see the "type_parser" method for how types, items, and symbols are handled
    """
    def __init__(self, id, type, glob, items=None, symbols=None, required=True, label=None,
                       description=None, fileTypes=None, outputEval=None, secondaryFiles=[]):
        self.id = check_id_hash(id)
        self.type = [type_parser(type, id, items, symbols)]
        if not required: self.type.insert(0, "null")
        self.create_output_binding(glob, outputEval, secondaryFiles)
        self.label = label
        self.description = description
        self.fileTypes = fileTypes

    def create_output_binding(self, glob, outputEval, secondaryFiles):
        self.outputBinding = Bindings()
        self.outputBinding.glob = expression_check(glob)
        if outputEval: self.outputBinding.outputEval = expression_check(outputEval)
        if not isinstance(secondaryFiles, list): secondaryFiles = [secondaryFiles]
        if secondaryFiles: self.outputBinding.secondaryFiles = [expression_check(value) for value in secondaryFiles]

class CwlArgument:
    """ CWL Arguments """
    def __init__(self, valueFrom, prefix=None, separate=False, position=0):
        self.valueFrom = expression_check(valueFrom)
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
    if id.startswith("#"): return id
    else: return "#" + id

def drop_hash(id):
    if id.startswith("#"): return id[1:]
    else: return id

def type_parser(type, id, items="File", symbols=[]):
    """ Check the type and parse appropriately """
    # note that complex arrays (e.g. arrays of enum) are not elegantly handled yet
    if type == "array": return {"type":"array", "items":items, "name":drop_hash(id)}
    elif type == "enum": return {"type":"enum", "symbols":symbols, "name":drop_hash(id)}
    elif type == "record": return {"type":"record", "fields":[], "name":drop_hash(id)}
    else: return str(type)

def expression_check(value, triggers=["'", "$"]):
    """
    Check if any js-triggering chars are in your value and return appropriate dict if True
        # Different ways the expression engine is triggered:
        #   the value for the key becomes the "new_value" dict
        #      e.g. stdin/out, output glob, file content, filename, components of the base command
        #   a 'class' has a 'value' that becomes the "new_value" dict
        #       e.g. in hints
        #   a 'class' has a 'valueFrom' that becomes the "new_value" dict
        #       e.g. input ports
    """
    if any(marker in str(value) for marker in triggers):
        return {"class": "Expression", "engine": "#cwl-js-engine", "script": value}
    else:
        return value

if __name__ == "__main__":

    # create cwl tool
    tool = CwlTool(id="test_tool", author="gaurav", label="testing123")
    tool.add_base_command("python test.py")
    tool.add_docker(dockerPull="ubuntu:latest")
    tool.add_stdout("$job.inputs.maybe.path + '.txt'")
    tool.add_computational_requirements(cpu="$job.inputs.maybe.size", mem=2000)

    # add input ports
    input1 = CwlInput(id="yes", type="array", items="int", required=False, prefix="-y")
    input2 = CwlInput(id="no", type="enum", symbols=["nope", "nuhhuh"], required=True, prefix="-n")
    input3 = CwlInput(id="maybe", type="File", prefix="-m", secondaryFiles=["^.bai", "$job.bai"])
    tool.object2input(input1)
    tool.object2input(input2)
    tool.object2argument(input3)

    # add arguments
    argument1 = CwlArgument(prefix="-r", valueFrom=30, separate=True, position=1)
    argument2 = CwlArgument(valueFrom="--verbose", position=99)
    tool.object2argument(argument1)
    tool.object2argument(argument2)

    # add output ports
    tool.object2output(CwlOutput(id="no", type="File", required=False, glob="*.txt"))

    # pretty print to console
    print(tool.object2json())

    # To run: python py2cwl.py | json2yaml