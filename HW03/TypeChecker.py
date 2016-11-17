#!/usr/bin/python
from collections import defaultdict

import AST
import SymbolTable

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

bin_op = ['|', '^', '&', '<<', '>>']
arithmetic_op = ['+', '-', '*', '/']
comparison_op = ['<', '>', '==', '!=', '<=', '>=']


for op in bin_op:
    ttype[op]['int']['int'] = 'int'

ttype['%']['int']['int'] = 'int'
ttype['=']['int']['int'] = 'int'
ttype['=']['float']['int'] = 'float'
ttype['=']['int']['float'] = 'float'
ttype['+']['string']['string'] = 'string'
ttype['*']['string']['int'] = 'string'

for op in arithmetic_op:
    ttype[op]['int']['int'] = 'int'
    ttype[op]['float']['float'] = 'float'
    ttype[op]['float']['int'] = 'float'
    ttype[op]['int']['float'] = 'float'

for op in comparison_op:
    ttype[op]['int']['int'] = 'int'
    ttype[op]['float']['float'] = 'int'
    ttype[op]['float']['int'] = 'int'
    ttype[op]['int']['float'] = 'int'
    ttype[op]['string']['string'] = 'int'







class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    # simpler version of generic_visit, not so general
    #def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)



class TypeChecker(NodeVisitor):

    def __init__(self):
        self.table = SymbolTable(None, "root")

    def visit_Program(self, node):
        self.visit(node.elements)

    def visit_Element(self, node):
        self.visit(node.dec)
        self.visit(node.func)
        self.visit(node.inst)

    def visit_Declaration(self, node):
        self.type = type
        self.visit(node.inits)

    def visit_Init(self, node):
        id_type = self.visit(node.ID)
        expr_type = self.visit(node.expr)
        if ttype['='][id_type][expr_type] is None:
            print 'Error: Assignment of {} to {}: line {}'.format(expr_type, id_type, node.line)
        else:
            if id_type is 'int' and expr_type is 'float':
                # write it better
                print 'Warning: Assignment of {} to {}: line {}'.format(expr_type, id_type, node.line)
            if self.table.get(node.name) is not None:
                print "Error: Variable '{}' already declared: line {}".format(node.ID, node.line)
            else:
                self.table.put(node.ID, id_type)

    def visit_PrintInstr(self, node):
        self.visit(node.expr_list)

    def visit_LabeledInstr(self, node):
        self.visit(node.instruction)

    def visit_Assignment(self, node):
        var_type = self.table.getAny(node.ID)
        expr_type = self.visit(node.expression)
        if var_type is None:
            print "Error: Usage of undeclared variable '{}': line {}".format(node.ID, node.line)
        elif ttype['='][var_type][expr_type] is None:
            print "Error: Illegal operation, {} = {}: line {}".format(var_type, expr_type, node.line)

    def visit_ChoiceInstr(self, node):
        self.visit(node.cond)
        self.visit(node.instr_1)
        if node.instr_2 is not None:
            self.visit(node.instr_2)

    def visit_WhileInstr(self, node):
        self.visit(node.cond)
        self.visit(node.instr)

    def visit_RepeatInstr(self, node):
        self.visit(node.instructions)
        self.visit(node.cond)

    # todo1
    def visit_ReturnInstr(self, node):
        pass

    def visit_RelExpr(self, node):
        type1 = self.visit(node.left)     # type1 = node.left.accept(self) 
        type2 = self.visit(node.right)    # type2 = node.right.accept(self)
        # ... 
        #

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_Variable(self, node):
        var_type = self.table.getAny(node.name)
        if var_type is None:
            print "Error: Usage of undeclared variable '{}': line {}".format(node.name, node.line)
        else:
            return type(var_type)

    def visit_IDPareExpr(self, node):
        fun_option = self.table.getAny(node.name)
        if not isinstance(fun_option, SymbolTable.FunctionSymbol):
            print "Error: Call of undefined fun '{}': line {}".format(node.name, node.line)
        else:
            # todo1
            pass

    def visit_PareExpr(self, node):
        return self.visit(node.expr)

    def visit_BinExpr(self, node):
                                          # alternative usage,
                                          # requires definition of accept method in class Node
        type1 = self.visit(node.left)     # type1 = node.left.accept(self)
        type2 = self.visit(node.right)    # type2 = node.right.accept(self)
        op    = node.op
        if ttype[op][type1][type2] is None:
            # todo1
            print "Error: Illegal operation, {} {} {}: line {}".format(type1, op, type2, node.line)
        return ttype[op][type1][type2]









