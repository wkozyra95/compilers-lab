

class Memory:

    # memory name
    def __init__(self, name):
        self.name = name
        self.mem_dict = {}

    # variable name
    def has_key(self, name):
        # todo
        pass

    # gets from memory current value of variable <name>
    def get(self, name):
        return None if name not in self.mem_dict.keys() else self.mem_dict[name]

    # puts into memory current value of variable <name>
    def put(self, name, value):
        self.mem_dict[name] = value


class MemoryStack:
    # initialize memory stack with memory <memory>
    def __init__(self, memory=None):
        self.stack = [Memory('root')] if memory is None else [memory]

    # gets from memory stack current value of variable <name>
    def get(self, name):
        self.stack.reverse()
        result = None
        for mem in self.stack:
            result = mem.get(name)
            if result is not None:
                break
        self.stack.reverse()
        return result

    # inserts into memory stack variable <name> with value <value>
    def insert(self, name, value):
        self.stack[-1].put(name, value)

    # sets variable <name> to value <value>
    def set(self, name, value):
        self.stack.reverse()
        for mem in self.stack:
            result = mem.get(name)
            if result is not None:
                mem.put(name, value)
                break
        self.stack.reverse()

    # pushes memory <memory> onto the stack
    def push(self, memory):
        self.stack.append(memory)

    # pops the top memory from the stack
    def pop(self):
        return self.stack.pop()


