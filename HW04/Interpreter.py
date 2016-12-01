
import AST
import operator
from Memory import *
from Exceptions import  *
from visit import *
import sys

sys.setrecursionlimit(10000)


class Interpreter(object):

    def __init__(self):
        self.mem_stack = MemoryStack()
        self.ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.div,
                    '%': operator.mod, '|': operator.or_, '&': operator.and_, '^': operator.xor,
                    'AND': operator.iand, 'OR': operator.ior, 'SHL': operator.lshift, 'SHR': operator.rshift,
                    'EQ': operator.eq, 'NEQ': operator.ne, '>': operator.gt, '<': operator.lt,
                    'LE': operator.le, 'GE': operator.ge}

    @on('node')
    def visit(self, node):
        pass

    @when(AST.Program)
    def visit(self, node):
        node.elements.accept(self)

    @when(AST.Elements)
    def visit(self, node):
        for elem in node.list:
            elem.accept(self)

    @when(AST.Element)
    def visit(self, node):
        node.dec.accept(self)
        node.func.accept(self)
        node.inst.accept(self)

    @when(AST.Declarations)
    def visit(self, node):
        for decl in node.list:
            decl.accept(self)

    @when(AST.Declaration)
    def visit(self, node):
        node.inits.accept(self)

    @when(AST.Inits)
    def visit(self, node):
        for init in node.list:
            init.accept(self)

    @when(AST.Init)
    def visit(self, node):
        expr = node.expr.accept(self)
        self.mem_stack.insert(node.ID, expr)

    @when(AST.Instructions)
    def visit(self, node):
        for inst in node.list:
            inst.accept(self)

    @when(AST.PrintInstr)
    def visit(self, node):
        print node.expr_list.accept(self)

    @when(AST.LabeledInstr)
    def visit(self, node):
        # todo ???
        pass

    @when(AST.Assignment)
    def visit(self, node):
        expr = node.expression.accept(self)
        self.mem_stack.set(node.ID, expr)
        return expr

    @when(AST.ChoiceInstr)
    def visit(self, node):
        if node.cond.accept(self):
            return node.instr_1.accept(self)
        elif node.indst_2 is not None:
            return node.instr_2.accept(self)

    # simplistic while loop interpretation
    @when(AST.WhileInstr)
    def visit(self, node):
        r = None
        while node.cond.accept(self):
            try:
                r = node.instr.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass
        return r

    @when(AST.RepeatInstr)
    def visit(self, node):
        r = None
        while True:
            try:
                r = node.instr.accept(self)
                # todo ???
                # if node.cond.accept(self):
                #    break
            except BreakException:
                break
            except ContinueException:
                pass
            if node.cond.accept(self):
                break
        return r

    @when(AST.ReturnInstr)
    def visit(self, node):
        value = node.expr.accept(self)
        raise ReturnValueException(value)

    @when(AST.ContinueInstr)
    def visit(self, node):
        raise ContinueException()

    @when(AST.BreakInstr)
    def visit(self, node):
        raise BreakException()

    @when(AST.CompoundInstr)
    def visit(self, node):
        node.declarations.accept(self)
        node.instructions_opt.accept(self)

    @when(AST.Const)
    def visit(self, node):
        return node.value
    """
    @when(AST.Integer)
    def visit(self, node):
        return node.value

    @when(AST.Float)
    def visit(self, node):
        return node.value

    @when(AST.String)
    def visit(self, node):
        return node.value
    """

    @when(AST.Variable)
    def visit(self, node):
        return self.mem_stack.get(node.name)

    @when(AST.IDPareExpr)
    def visit(self, node):
        function = self.mem_stack.get(node.name)
        fun_mem = Memory(node.name)
        for arg, expr in zip(function.args_list.list, node.expr_list.list):
            fun_mem.put(arg.accept(self), expr.accept(self))
        self.mem_stack.push(fun_mem)
        try:
            function.compound_instr.accept(self)
        except ReturnValueException as e:
            return e.value
        self.mem_stack.pop()

    @when(AST.PareExpr)
    def visit(self, node):
        return node.expr.accept(self)

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        return self.ops[node.op](r1, r2)

    @when(AST.ExprList)
    def visit(self, node):
        for expr in node.list:
            expr.accept(self)

    @when(AST.FunDefs)
    def visit(self, node):
        for fun_def in node.list:
            fun_def.accept(self)

    @when(AST.FunDef)
    def visit(self, node):
        # todo ???
        self.mem_stack.insert(node.ID, node)

    @when(AST.ArgsList)
    def visit(self, node):
        for arg in node.list:
            arg.accept(self)

    @when(AST.Arg)
    def visit(self, node):
        return node.name

    # todo ???
    """
    @when(AST.RelOp)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        # ...
    """