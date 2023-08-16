#!/usr/bin/env python3

import fire
import re
import subprocess
from typing import Optional


def help_to_asciidoc(script: str):

    result = subprocess.run([script, '--help'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='UTF-8')

    text = result.stdout

    sections = {
        'name': '',
        'synopsis': '',
        'description': '',
        'arguments': [],
        'flags': [],
        'notes': '',
    }

    last_section: Optional[str] = None
    for line in re.split('\n', text):
        # print(line)
        if re.match(r'^NAME', string=line):
            last_section = 'name'

        elif re.match(r'SYNOPSIS', string=line):
            last_section = 'synopsis'

        elif re.match(r'DESCRIPTION', string=line):
            last_section = 'description'

        elif re.match(r'POSITIONAL ARGUMENTS', string=line):
            last_section = 'arguments'

        elif re.match(r'FLAGS', string=line):
            last_section = 'flags'

        elif re.match(r'NOTES', string=line):
            last_section = 'notes'

        elif last_section in ['arguments', 'flags']:
            if m := re.match(r'\s{4}(\S.*)', line):
                sections[last_section].append({
                    'name': m[1].lstrip(),
                    'type': '',
                    'description': '',
                })

            elif m := re.match(r'\s{8}Type: (\w+)', line):
                sections[last_section][-1]['type'] = m[1].lstrip()

            elif m := re.match(r'\s{8}Default: (\S.*)', line):
                sections[last_section][-1]['default'] = m[1].lstrip()

            elif m := re.match(r'\s{8}(\S.*)', line):
                sections[last_section][-1]['description'] = m[1].lstrip().replace('\n', '\n\n')

        elif last_section is not None:
            if len(line.strip()):
                sections[last_section] += ('\n' if sections[last_section] else '') + line.lstrip()
            else:
                sections[last_section] += '\n'

    if (l := re.split(r'\s+-\s+', sections['name'])) and len(l) > 1:
        # print(l)
        sections['name'] = l[0]
        sections['short_description'] = l[1]

    ascii_doc = '= {name}\n\n'.format(name=sections['name'])

    if 'short_description' in sections:
        ascii_doc += sections['short_description'] + '\n\n'

    if sections['synopsis']:
        ascii_doc += '== Synopsis\n\n    {synopsis}\n\n'.format(synopsis=sections['synopsis'])

    if sections['description']:
        ascii_doc += '== Description\n\n{description}\n\n'.format(description=sections['description'])

    if sections['arguments'] or sections['flags']:
        ascii_doc += '== Parameters\n\n'
        for arg in sections['arguments']:
            ascii_doc += '{name} [{type}]:: {description}\n\n'.format(**arg)

        for flag in sections['flags']:
            ascii_doc += '{name} [{type}]:: {description} (default: {default})\n\n'.format(**flag)

    return ascii_doc


if __name__ == "__main__":
    fire.Fire(help_to_asciidoc)
