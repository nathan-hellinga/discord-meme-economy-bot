class CommandParse:

    def __init__(self, dev=False):
        self.commands =[]
        self.dev = dev

    def add_command(self, key, method, description, dev=False):
        self.commands.append(Command(key, method, description, dev))

    def parse(self, string):
        string = string.lower()
        segments = string.split(' ')
        for i in self.commands:
            # check for key match
            if segments[0] == i.key:
                # check for permissions
                if i.dev is False or (i.dev is True and self.dev is True):
                    return i.method
        return None


    def list(self):
        msg = ""
        for i in self.commands:
            if i.dev is False or (i.dev is True and self.dev is True):
                temp = "\t`{}` - {}\n".format(i.key, i.description)
                msg += temp
        return msg


class Command:

    def __init__(self, key, method, description, dev):
        self.key = key
        self.method = method
        self.description = description
        self.dev = dev
