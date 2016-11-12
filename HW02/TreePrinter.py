
import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.Program)
    def printTree(self, indent=0):
        return "" if self.elements is None else self.elements.printTree(indent)

    @addToClass(AST.Elements)
    def printTree(self, indent=0):
        res = ""
        for element in self.list:
            res += "" if element is None else element.printTree(indent)
        return res

    @addToClass(AST.Element)
    def printTree(self, indent=0):
        return ("" if self.dec is None else self.dec.printTree(indent)) + \
        ("" if self.func is None else self.func.printTree(indent)) + \
        ("" if self.inst is None else self.inst.printTree(indent))

    @addToClass(AST.Declarations)
    def printTree(self, indent=0):
        res = "| " * indent + "DECL\n"
        for dec in self.list:
            res += "" if dec is None else dec.printTree(indent+1)
        return res

    @addToClass(AST.Declaration)
    def printTree(self, indent=0):
        return self.inits.printTree(indent)

    @addToClass(AST.Inits)
    def printTree(self, indent=0):
        res = ""
        for init in self.list:
            res += "" if init is None else init.printTree(indent)
        return res

    @addToClass(AST.Init)
    def printTree(self, indent=0):
        return "| " * indent + "=\n" + \
            "| " * (indent+1) + self.ID + "\n" + \
            self.expr.printTree(indent+1)

    @addToClass(AST.Instructions)
    def printTree(self, indent=0):
        res = ""
        for instr in self.list:
            res += instr.printTree(indent)
        return res

    @addToClass(AST.PrintInstr)
    def printTree(self, indent=0):
        return "| " * indent + "PRINT\n" + \
            self.expr_list.printTree(indent+1)

    @addToClass(AST.LabeledInstr)
    def printTree(self, indent=0):
        return "| " * indent + "LABEL\n" + \
            "| " * (indent+1) + str(self.ID) + "\n" + \
            self.instruction.printTree(indent+1)
        # return "| " * indent + str(self.ID) + "\n" + \
        #     self.instruction.printTree(indent+1)

    @addToClass(AST.Assignment)
    def printTree(self, indent=0):
        return "| " * indent + "=\n" + \
            "| " * (indent+1) + str(self.ID) + "\n" + \
            self.expression.printTree(indent+1)

    @addToClass(AST.ChoiceInstr)
    def printTree(self, indent=0):
        res = "| " * indent + "IF\n" + \
            self.cond.printTree(indent+1) + \
            self.instr_1.printTree(indent+1) # +1
        if self.instr_2 is not None:
            res += "| " * indent + "ELSE\n" + \
                self.instr_2.printTree(indent+1) # +1
        return res

    @addToClass(AST.WhileInstr)
    def printTree(self, indent=0):
        return "| " * indent + "WHILE\n" + \
            self.cond.printTree(indent+1) + \
            self.instr.printTree(indent+1)

    @addToClass(AST.RepeatInstr)
    def printTree(self, indent=0):
        return "| " * indent + "REPEAT\n" + \
            self.instructions.printTree(indent+1) + \
            "| " * indent + "UNTIL\n" + \
            self.cond.printTree(indent+1)

    @addToClass(AST.ReturnInstr)
    def printTree(self, indent=0):
        return "| " * indent + "RETURN\n" + \
            self.expr.printTree(indent+1)

    @addToClass(AST.ContinueInstr)
    def printTree(self, indent=0):
        return "| " * indent + "CONTINUE\n"

    @addToClass(AST.BreakInstr)
    def printTree(self, indent=0):
        return "| " * indent + "BREAK\n"

    @addToClass(AST.CompoundInstr)
    def printTree(self, indent=0):
        res = ""
        if self.declarations is not None:
            res += self.declarations.printTree(indent) # +1
        res += self.instructions_opt.printTree(indent) # +1
        return res

    @addToClass(AST.Const)
    def printTree(self, indent=0):
        return "| " * indent + str(self.const) + "\n"

    @addToClass(AST.PareExpr)
    def printTree(self, indent=0):
        return self.expr.printTree(indent)

    @addToClass(AST.IDPareExpr)
    def printTree(self, indent=0):
        return "| " * indent + "FUNCALL\n" + \
            "| " * (indent+1) + str(self.ID) + "\n" + \
            self.expr_list.printTree(indent+1) # -1

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        return "| " * indent + str(self.op) + "\n" + \
            self.left.printTree(indent+1) + \
            self.right.printTree(indent+1)

    @addToClass(AST.ExprList)
    def printTree(self, indent=0):
        res = ""
        for expr in self.list:
            res += expr.printTree(indent) # +1
        return res

    @addToClass(AST.FunDefs)
    def printTree(self, indent=0):
        res = ""

        for fundef in self.list:
            res += fundef.printTree(indent)

        return res

    @addToClass(AST.FunDef)
    def printTree(self, indent=0):
        return "| " * indent + "FUNDEF\n" + \
            "| " * (indent+1) + str(self.ID) + "\n" + \
            "| " * (indent+1) + "RET " + str(self.type) + "\n" + \
            self.args_list.printTree(indent+1) + self.compound_instr.printTree(indent+1) # -1

    @addToClass(AST.ArgsList)
    def printTree(self, indent=0):
        res = ""
        for arg in self.list:
            res += arg.printTree(indent)
        return res

    @addToClass(AST.Arg)
    def printTree(self, indent=0):
        return "| " * indent + "ARG " + str(self.ID) + "\n"


