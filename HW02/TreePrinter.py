
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


    @addToClass(AST.BinExpr)
    def printTree(self):
        pass
        # ...

    @addToClass(AST.Program)
    def printTree(self, indent = 0):
        print 'PROGRAM'
        for e in self.dec:
            e.printTree(indent)

    @addToClass(AST.Declaration)
    def printTree(self, indent):
        print '|' * indent + 'DECL'
        for e in self.inits:
            e.printTree(indent + 1)

    # @addToClass ...
    # ...
