
import AST
import math
import operator
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys

sys.setrecursionlimit(10000)


class Interpreter(object):

    def __init__(self):
        self.mem_stack = MemoryStack()
        self.ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.div}

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
        expr = node.expr.accepr(self)
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
        while node.cond.accept(self):
            try:
                r = node.instr.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass
        return r












    @when(AST.BinOp)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        return self.ops[node.op](r1, r2)


    # todo ???
    @when(AST.RelOp)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        # ...


    #

    @when(AST.Const)
    def visit(self, node):
        return node.value



    @when(AST.BreakInstr)
    def visit(self, node):
        raise BreakException()

    @when(AST.ContinueInstr)
    def visit(self, node):
        raise ContinueException()
