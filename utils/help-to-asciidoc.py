#!/usr/bin/env python3
from os.path import join, isfile, basename
import fire
import re
import subprocess
from typing import Optional


def parse_help(script: str) -> dict:

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

    return sections


def sections_to_asciidoc(sections: dict) -> str:
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


def get_python_scripts(script_path: str, doc_path: str, adoc_file: str):
    import glob

    scripts = {}
    for s in [basename(file) for file in glob.glob(join(script_path, 'dt-*')) if isfile(file) and basename(file) not in ['dt-qt.py', 'dt-gui.py']]:
        f = open(join(script_path, s), 'r')
        if f.readline().strip() in ['#!/usr/bin/python3', '#!/usr/bin/env python3']:
            scripts[s] = parse_help(join(script_path, s))

    adoc = open(join(doc_path, adoc_file), 'w')
    adoc.write("""= Script Documentation
:icons:font

""")

    for script in sorted(scripts.keys()):
        script_adoc_file = join(doc_path, script + '.adoc')
        adoc.write('* xref:%s[`%s`]' % (script + '.adoc', script))
        if 'short_description' in scripts[script]:
            adoc.write(' -- %s' % scripts[script]['short_description'].strip())

        adoc.write('\n\n')

        with open(script_adoc_file, 'w') as script_adoc:
            script_adoc.write(sections_to_asciidoc(scripts[script]))


if __name__ == "__main__":
    fire.Fire(get_python_scripts)
