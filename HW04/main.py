import sys
import ply.yacc as yacc
from Cparser import Cparser
import Interpreter as inter
from TypeChecker import TypeChecker


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    Cparser = Cparser()
    parser = yacc.yacc(module=Cparser)
    text = file.read()

    ast = parser.parse(text, lexer=Cparser.scanner)
    
    typeChecker = TypeChecker()
    ast.accept(typeChecker)

    print "Type correct"

    ast.accept(inter.Interpreter())

    # new

    print "End checking"
