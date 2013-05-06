import os

class CodeListing(object):
    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
        self.was_written = False



class Command(unicode):
    def __init__(self, a_string):
        self.was_run = False
        unicode.__init__(a_string)



class Output(unicode):
    def __init__(self, a_string):
        self.was_checked = False
        unicode.__init__(a_string)



def parse_listing(listing):
    if listing.getnext().get('class') == 'paragraph caption':
        filename = listing.getnext().text_content()
        contents = listing.text_content().strip().replace('\r\n', '\n')
        return [CodeListing(filename, contents)]

    else:
        commands = get_commands(listing)
        lines = listing.text_content().strip().replace('\r\n', '\n').split('\n')
        outputs = []
        output_after_command = ''
        for line in lines:
            commands_in_this_line = filter(line.endswith, commands)
            if commands_in_this_line:
                if output_after_command:
                    outputs.append(Output(output_after_command.rstrip()))
                    output_after_command = ''
                outputs.append(Command(commands_in_this_line[0]))
            else:
                output_after_command += line + '\n'
        if output_after_command:
            outputs.append(Output(output_after_command.rstrip()))
        return outputs


def get_commands(node):
    commands = [
        el.text_content()
        for el in node.cssselect('pre code strong')
    ]
    if commands.count("git rm --cached superlists/"):
        ## hack -- listings with a star in are weird
        fix_pos = commands.index("git rm --cached superlists/")
        commands.remove("git rm --cached superlists/")
        commands.remove(".pyc")
        commands.insert(fix_pos, "git rm --cached superlists/*.pyc")

    return commands


def write_to_file(codelisting, cwd):
    if "[..." not in codelisting.contents:
        new_contents = codelisting.contents
    else:
        with open(os.path.join(cwd, codelisting.filename)) as f:
            old_contents = f.read()
        lines = codelisting.contents.split('\n')
        split_line = [l for l in lines if "[..." in l][0]
        indent = split_line.split("[...")[0]
        split_line_pos = lines.index(split_line)
        lines_before = lines[:split_line_pos]
        last_line_before = lines_before[-1]
        lines_after = lines[split_line_pos + 1:]

        old_lines = old_contents.split('\n')
        last_old_line = [
            l for l in old_lines if l.strip() == last_line_before.strip()
        ][0]
        last_old_line_pos = old_lines.index(last_old_line)
        old_lines_after = old_lines[last_old_line_pos + 1:]

        new_contents = '\n'.join(lines_before)
        newline_indent = '\n' + indent
        new_contents += newline_indent
        new_contents += newline_indent.join(old_lines_after)
        new_contents += '\n'
        new_contents += '\n'.join(lines_after)

    new_contents = '\n'.join(
        l.rstrip(' #') for l in new_contents.split('\n')
    )

    with open(os.path.join(cwd, codelisting.filename), 'w') as f:
        f.write(new_contents)

    codelisting.was_written = True

