
class Node(object):

    def __str__(self):
        return self.printTree()


class BinExpr(Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Const(Node):
    def __init__(self, value):
        self.value = value
    pass
    #...

class Integer(Const):
    pass
    #...


class Float(Const):
    pass
    #...


class String(Const):
    pass
    #...


class Variable(Node):
    pass
    #...

class Program(Node):
    def __init__(self, dec, func, inst):
        self.dec = dec
        self.func = func
        self.inst = inst

class Declaration(Node):
    def __init__(self, type, inits):
        self.type = type
        self.inits = inits

# ...


