
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
                    '==': operator.eq, '!=': operator.ne, '>': operator.gt, '<': operator.lt,
                    '<=': operator.le, '>=': operator.ge}

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
        if node.dec is not None:
            node.dec.accept(self)
        if node.func is not None:
            node.func.accept(self)
        if node.inst is not None:
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
        for expr in node.expr_list.list:
            print expr.accept(self)

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
        elif node.instr_2 is not None:
            return node.instr_2.accept(self)

    # simplistic while loop interpretation
    @when(AST.WhileInstr)
    def visit(self, node):
        while node.cond.accept(self):
            try:
               node.instr.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass

    @when(AST.RepeatInstr)
    def visit(self, node):
        while True:
            try:
                node.instructions.accept(self)
                if node.cond.accept(self):
                    break
            except BreakException:
                break
            except ContinueException:
                pass
            if node.cond.accept(self):
                break

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
        fun_mem = Memory('compound')
        self.mem_stack.push(fun_mem)
        if node.declarations is not None:
            node.declarations.accept(self)
        node.instructions_opt.accept(self)
        self.mem_stack.pop()

    @when(AST.Const)
    def visit(self, node):
        return node.const.accept(self)

    @when(AST.Integer)
    def visit(self, node):
        return int(node.const)

    @when(AST.Float)
    def visit(self, node):
        return node.const

    @when(AST.String)
    def visit(self, node):
        return node.const

    @when(AST.Variable)
    def visit(self, node):
        return self.mem_stack.get(node.name)

    @when(AST.IDPareExpr)
    def visit(self, node):
        function = self.mem_stack.get(node.ID)
        fun_mem = Memory(node.ID)
        if node.expr_list is not None:
            for arg, expr in zip(function.args_list.list, node.expr_list.list):
                fun_mem.put(arg.accept(self), expr.accept(self))
        
        self.mem_stack.push(fun_mem)
        try:
            function.compound_instr.accept(self)
        except ReturnValueException as e:
            self.mem_stack.pop()
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
        self.mem_stack.insert(node.ID, node)

    @when(AST.ArgsList)
    def visit(self, node):
        for arg in node.list:
            arg.accept(self)

    @when(AST.Arg)
    def visit(self, node):
        return node.ID

    # todo ???
    """
    @when(AST.RelOp)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        # ...
    """
