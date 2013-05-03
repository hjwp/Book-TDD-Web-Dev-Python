
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
        contents = listing.text_content().strip()
        return [CodeListing(filename, contents)]

    else:
        commands = get_commands(listing)
        lines = listing.text_content().strip().split('\r\n')
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
                output_after_command += line + '\r\n'
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
