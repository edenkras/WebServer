import re
from os.path import isfile

import webserver.admin

from settings import TemplatesFolder


def parser(htmlFile, admin=False, **kwargs):
	if htmlFile[htmlFile.rfind('.')+1:] != 'html':
		raise Exception('HTML file expected, instead got: ' + htmlFile)
	if admin:
		adminPath = webserver.admin.__file__
		path = adminPath[:adminPath.rfind('\\')+1] + 'Templates'
	else:
		path = TemplatesFolder
	path += '\\' + htmlFile
	if not isfile(path):
		raise Exception('No such HTML file: ' + htmlFile)

	content = ''
	with open(path, 'r', encoding='utf8') as f:
		command = ''
		lines = []
		for line in f.readlines():
			code = re.findall('{\((.*)\)}', line)
			code = code[0].strip() if len(code) != 0 else ''
			if code and not code.startswith('end'):
				command = code
			elif code == 'end' + command.split(' ')[0]:
				content += executeCommand(command, lines, kwargs)
				command = ''
				lines = []
			elif command != '':
				lines.append(line)
			else:
				content += parseLine(line, kwargs)
	return content.encode()

def parseLine(line, vars):
	for var in re.findall('{{(.*?)}}', line):
		if var in vars:
			line = line.replace('{{' + var + '}}', str(vars[var]))
	return line

def executeCommand(command, lines, vars):
	command = 'output = \'\'\n' + command
	command += '\n\tfor line in lines:'
	command += '\n\t\toutput += parseLine(line, {**locals(), **vars})'
	final = {}
	exec(command, {**vars, 'lines': lines, 'vars': vars, 'parseLine': parseLine}, final)
	return final['output']
