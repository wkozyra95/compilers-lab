
class Node(object):

    def accept(self, visitor):
        return visitor.visit(self)

    def __str__(self):
        return self.printTree()


class Program(Node):
    def __init__(self, elements):
        self.elements = elements


class Elements(Node):
    def __init__(self):
        self.list = []

    def add(self, dec):
        self.list.append(dec)


class Element(Node):
    def __init__(self, dec, func, inst):
        self.dec = dec
        self.func = func
        self.inst = inst


class Declarations(Node):
    def __init__(self):
        self.list = []

    def add(self, dec):
        self.list.append(dec)


class Declaration(Node):
    def __init__(self, type, inits):
        self.type = type
        self.inits = inits


class Inits(Node):
    def __init__(self):
        self.list = []

    def add(self, init):
        self.list.append(init)


class Init(Node):
    def __init__(self, ID, expr):
        self.ID = ID
        self.expr = expr


class Instructions(Node):
    def __init__(self):
        self.list = []

    def add(self, init):
        self.list.append(init)


class PrintInstr(Node):
    def __init__(self, expr_list):
        self.expr_list = expr_list


class LabeledInstr(Node):
    def __init__(self, ID, instruction):
        self.ID = ID
        self.instruction = instruction


class Assignment(Node):
    def __init__(self, ID, expression):
        self.ID = ID
        self.expression = expression


class ChoiceInstr(Node):
    def __init__(self, cond, instr_1, instr_2):
        self.cond = cond
        self.instr_1 = instr_1
        self.instr_2 = instr_2


class WhileInstr(Node):
    def __init__(self, cond, instr):
        self.cond = cond
        self.instr = instr


class RepeatInstr(Node):
    def __init__(self, instructions, cond):
        self.instructions = instructions
        self.cond = cond


class ReturnInstr(Node):
    def __init__(self, expr):
        self.expr = expr


class ContinueInstr(Node):
    pass


class BreakInstr(Node):
    pass


class CompoundInstr(Node):
    def __init__(self, declarations, instructions_opt):
        self.declarations = declarations
        self.instructions_opt = instructions_opt


class Const(Node):
    def __init__(self, const):
        self.const = const


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
    def __init__(self, line, name):
        self.name = name


class IDPareExpr(Node):
    def __init__(self, ID, expr_list):
        self.ID = ID
        self.expr_list = expr_list


class PareExpr(Node):
    def __init__(self, expr):
        self.expr = expr


class BinExpr(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class ExprList(Node):
    def __init__(self):
        self.list = []

    def add(self, expr):
        self.list.append(expr)


class FunDefs(Node):
    def __init__(self):
        self.list = []

    def add(self, fundef):
        self.list.append(fundef)


class FunDef(Node):
    def __init__(self, type, ID, args_list, compound_instr):
        self.type = type
        self.ID = ID
        self.args_list = args_list
        self.compound_instr = compound_instr


class ArgsList(Node):
    def __init__(self):
        self.list = []

    def add(self, arg):
        self.list.append(arg)


class Arg(Node):
    def __init__(self, type, ID):
        self.type = type
        self.ID = ID

