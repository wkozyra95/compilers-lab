#!/usr/bin/python
from collections import defaultdict

from AST import *
from SymbolTable import *

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
ttype['=']['string']['string'] = 'string'
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
            #
            if node is None:
                return
            for child in node.list:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, Node):
                            self.visit(item)
                elif isinstance(child, Node):
                    self.visit(child)

    # simpler version of generic_visit, not so general
    #def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)



class TypeChecker(NodeVisitor):

    def __init__(self):
        self.table = SymbolTable(None, "root")
        self.function = None
        self.type = None
        self.loop = []

    def visit_Program(self, node):
        self.visit(node.elements)

    def visit_Element(self, node):
        self.visit(node.dec)
        self.visit(node.func)
        self.visit(node.inst)

    def visit_Declaration(self, node):
        self.type = node.type
        self.visit(node.inits)
        self.type = None

    def visit_Init(self, node):
        id_type = self.type
        expr_type = self.visit(node.expr)

        if ttype['='][id_type][expr_type] is None:
            print 'Error: Assignment of {} to {}: line {}'.format(expr_type, id_type, node.line)
        else:
            if id_type is 'int' and expr_type is 'float':
                print 'Warning: Assignment of {} to {}: line {}'.format(expr_type, id_type, node.line)

            if isinstance(self.table.getAny(node.ID), FunctionSymbol):
                    print "Error: Function identifier '{}' used as a variable: line {}".format(node.ID, node.line)
            elif self.table.get(node.ID) is not None:
                print "Error: Variable '{}' already declared: line {}".format(node.ID, node.line)
            else:
                self.table.put(node.ID, VariableSymbol(node.ID, id_type))

    def visit_PrintInstr(self, node):
        self.visit(node.expr_list)

    def visit_LabeledInstr(self, node):
        self.visit(node.instruction)

    def visit_Assignment(self, node):
        var_type = self.table.getAny(node.ID)
        expr_type = self.visit(node.expression)
        if var_type is None:
            print "Error: Variable '{}' undefined in current scope: line {}".format(node.ID, node.line)
        elif isinstance(var_type, FunctionSymbol):
            print "Error: Function identifier '{}' used as a variable: line {}".format(node.ID, node.line)
        elif ttype['='][var_type.type][expr_type] is None and var_type.type is not None and expr_type is not None:
            print "Error: Illegal operation, {} = {}: line {}".format(var_type.type, expr_type, node.line)

    def visit_ChoiceInstr(self, node):
        self.visit(node.cond)
        self.visit(node.instr_1)
        if node.instr_2 is not None:
            self.visit(node.instr_2)

    def visit_WhileInstr(self, node):
        self.visit(node.cond)
        self.loop.append(1)
        self.visit(node.instr)
        self.loop.pop()

    def visit_RepeatInstr(self, node):
        self.loop.append(1)
        self.visit(node.instructions)
        self.loop.pop()
        self.visit(node.cond)

    def visit_ReturnInstr(self, node):
        if self.function is None:
            print "Error: return instruction outside a function: line {}".format(node.line)
        else:
            self.function.ret = 1
            expr_type = self.visit(node.expr)
            if ttype['='][self.function.type][expr_type] is None and self.function.type is not None and expr_type is not None:
                print "Error: Improper returned type, expected {}, got {}: line {}".format(self.function.type, expr_type, node.line)

    def visit_ContinueInstr(self, node):
        if len(self.loop) == 0:
            print "Error: continue instruction utside a loop: line {}".format(node.line)

    def visit_BreakInstr(self, node):
        if len(self.loop) == 0:
            print "Error: break instruction outside a loop: line {}".format(node.line)

    def visit_CompoundInstr(self, node):
        new_table = SymbolTable(self.table, "child")
        self.table = new_table
        if node.declarations is not None:
            self.visit(node.declarations)
        self.visit(node.instructions_opt)
        self.table = self.table.getParentScope()

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_Const(self, node):
        return self.visit(node.const)

    def visit_Variable(self, node):
        var_type = self.table.getAny(node.name)
        if var_type is None:
            print "Error: Usage of undeclared variable '{}': line {}".format(node.name, node.line)
        elif isinstance(var_type, FunctionSymbol):
            print "Error: Function identifier '{}' used as a variable: line {}".format(node.name, node.line)
        else:
            return var_type.type

    def visit_IDPareExpr(self, node):
        fun_option = self.table.getAny(node.ID)
        if not isinstance(fun_option, FunctionSymbol):
            print "Error: Call of undefined fun '{}': line {}".format(node.ID, node.line)
        else:
            if len(node.expr_list.list) != len(fun_option.parameters):
                print "Error: Improper number of args in {} call: line {}".format(fun_option.name, node.line)
            else:
                args_types = [self.visit(arg_type) for arg_type in node.expr_list.list]
                declared_types = fun_option.parameters
                for (declared, current) in zip(args_types, declared_types):
                    if ttype['='][declared][current] is None:
                        print "Error: Improper type of args in {} call: line {}".format(fun_option.name, node.line)
                        break
            return fun_option.type

    def visit_PareExpr(self, node):
        return self.visit(node.expr)

    def visit_BinExpr(self, node):
                                          # alternative usage,
                                          # requires definition of accept method in class Node
        type1 = self.visit(node.left)     # type1 = node.left.accept(self)
        type2 = self.visit(node.right)    # type2 = node.right.accept(self)
        op = node.op
        if ttype[op][type1][type2] is None and type1 is not None and type2 is not None:
            print "Error: Illegal operation, {} {} {}: line {}".format(type1, op, type2, node.line)
        return ttype[op][type1][type2]

    def visit_FunDef(self, node):
        fun_name = self.table.get(node.ID)
        if fun_name is not None:
            print "Error: Redefinition of function '{}': line {}".format(node.ID, node.line)
        else:
            new_table = SymbolTable(self.table, "child")
            function = FunctionSymbol(node.ID, node.type, new_table)
            self.function = function
            self.table.put(node.ID, function)
            self.table = function.table
            if node.args_list is not None:
                self.visit(node.args_list)
            self.visit(node.compound_instr)
            self.table = self.table.getParentScope()
            if self.function.ret == 0:
                print "Error: Missing return statement in function '{}' returning {}: line {}".format(self.function.name, self.function.type, node.line)
            self.function = None

    def visit_ArgsList(self, node):
        for arg in node.list:
            self.visit(arg)
        self.function.extract()

    def visit_Arg(self, node):
        if self.table.get(node.ID) is not None:
            print "Error: Variable '{}' already declared: line {}".format(node.ID, node.line)
        else:
            self.table.put(node.ID, VariableSymbol(node.ID, node.type))
