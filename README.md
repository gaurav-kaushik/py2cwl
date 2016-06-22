#py2cwl-writer

##Usage
**Command:** `python py2cwl.py | json_reformat > <file.cwl>`

To get the json_reformat tool, use:
	`brew install yajl` (Mac OSX) or `apt-get install yajl-tools` (Linux)

Can convert to (messy) YAML with json2yaml (`brew install json2yaml`): `python py2cwl.py | json_reformat | json2yaml > <file.yml>`
