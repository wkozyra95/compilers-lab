#!/usr/bin/python


class Symbol(object):
    pass


class VariableSymbol(Symbol):

    def __init__(self, name, type):
        self.name = name
        self.type = type
    #

class FunctionSymbol(Symbol):

    def __init__(self, name, type, table):
        self.type = type
        self.name = name
        self.parameters = []
        self.table = table

    def extract(self):
        self.parameters = [x.type for x in self.table.table.values()]


class SymbolTable(object):

    def __init__(self, parent, name, ): # parent scope and symbol table name
        self.parent = parent
        self.name = name
        self.table = {}

    #

    def put(self, name, symbol): # put variable symbol or fundef under <name> entry
        self.table[name] = symbol
    #

    def get(self, name): # get variable symbol or fundef from <name> entry
        if name in self.table.keys():
            return self.table[name]
        else:
            return None
    #

    def getAny(self, name):
        var_type = self.get(name)
        if var_type is not None:
            return var_type
        else:
            if self.parent is not None:
                return self.parent.getAny(name)

    def getParentScope(self):
        return self.parent
    #

    def pushScope(self, name):
        pass
    #

    def popScope(self):
        pass
    #


