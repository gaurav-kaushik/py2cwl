#py2cwl

##Usage

### Python to CWL JSON
	`python py2cwlwriter.py | json_reformat > <file.cwl>`

-
### Python to CWL YAML (messy)
	`python py2cwlwriter.py | json_reformat | json2yaml > <file.yml>`

### JSON/YAML tools
**json_reformat**:

Mac: `brew install yajl`

Linux: `apt-get install yajl-tools`

**json2yaml**:

Mac: `brew install json2yaml` 

Node: `npm install -g json2yaml`
