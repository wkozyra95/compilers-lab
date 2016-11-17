#!/usr/bin/python

from scanner import Scanner
import AST



class Cparser(object):


    def __init__(self):
        self.scanner = Scanner()
        self.scanner.build()

    tokens = Scanner.tokens


    precedence = (
       ("nonassoc", 'IFX'),
       ("nonassoc", 'ELSE'),
       ("right", '='),
       ("left", 'OR'),
       ("left", 'AND'),
       ("left", '|'),
       ("left", '^'),
       ("left", '&'),
       ("nonassoc", '<', '>', 'EQ', 'NEQ', 'LE', 'GE'),
       ("left", 'SHL', 'SHR'),
       ("left", '+', '-'),
       ("left", '*', '/', '%'),
    )


    def p_error(self, p):
        if p:
            print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')".format(p.lineno, self.scanner.find_tok_column(p), p.type, p.value))
        else:
            print("Unexpected end of input")


    def p_program(self, p):
        """program : elements"""
        program = AST.Program(None if len(p[1].list) == 0 else p[1])
        p[0] = program
        # print program


    def p_elements(self, p):
        """elements : elements element
                    | """
        if len(p) == 1:
            p[0] = AST.Elements()
        else:
            p[0] = AST.Elements() if p[1] is None else p[1]
            p[0].add(p[2])


    def p_element(self, p):
        """element : declarations fundefs_opt instructions_opt"""
        p[0] = AST.Element(None if len(p[1].list) == 0 else p[1], None if len(p[2].list) == 0 else p[2],
                           None if len(p[3].list) == 0 else p[3])


    def p_declarations(self, p):
        """declarations : declarations declaration
                        | """
        if len(p) == 1:
            p[0] = AST.Declarations()
        else:
            p[0] = AST.Declarations() if p[1] is None else p[1]
            p[0].add(p[2])


    def p_declaration(self, p):
        """declaration : TYPE inits ';'
                       | error ';' """
        if len(p) == 4:
            p[0] = AST.Declaration(p[1], p[2])


    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        if len(p) == 4:
            p[0] = AST.Inits() if p[1] is None else p[1]
            p[0].add(p[3])
        else:
            p[0] = AST.Inits()
            p[0].add(p[1])


    def p_init(self, p):
        """init : ID '=' expression """
        p[0] = AST.Init(p[1], p[3], p.lineno(1))


    def p_instructions_opt(self, p):
        """instructions_opt : instructions
                            | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = AST.Instructions()

    def p_instructions(self, p):
        """instructions : instructions instruction
                        | instruction """
        if len(p) == 2:
            p[0] = AST.Instructions()
            p[0].add(p[1])
        else:
            p[0] = AST.Instructions() if p[1] is None else p[1]
            p[0].add(p[2])

    def p_instruction(self, p):
        """instruction : print_instr
                       | labeled_instr
                       | assignment
                       | choice_instr
                       | while_instr
                       | repeat_instr
                       | return_instr
                       | break_instr
                       | continue_instr
                       | compound_instr
                       | expression ';' """
        p[0] = p[1]

    def p_print_instr(self, p):
        """print_instr : PRINT expr_list ';'
                       | PRINT error ';' """
        p[0] = AST.PrintInstr(p[2], p.lineno(1))


    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = AST.LabeledInstr(p[1], p[3])


    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        p[0] = AST.Assignment(p[1], p[3], p.lineno(1))

    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' error ')' instruction  %prec IFX """
        p[0] = AST.ChoiceInstr(p[3], p[5], None)


    def p_choice_instr_else(self, p):
        """choice_instr : IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction ELSE instruction """
        p[0] = AST.ChoiceInstr(p[3], p[5], p[7])


    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        p[0] = AST.WhileInstr(p[3], p[5])


    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT instructions UNTIL condition ';' """
        p[0] = AST.RepeatInstr(p[2], p[4])


    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = AST.ReturnInstr(p[2], p.lineno(1))


    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = AST.ContinueInstr()


    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = AST.BreakInstr()


    def p_compound_instr(self, p):
        """compound_instr : '{' declarations instructions_opt '}' """
        p[0] = AST.CompoundInstr(None if len(p[2].list) == 0 else p[2], p[3])


    def p_condition(self, p):
        """condition : expression"""
        # p[0] = AST.Condition(p[1])
        p[0] = p[1]


    def p_const_int(self, p):
        """const : INTEGER"""
        p[0] = AST.Integer(p[1], p.lineno(1))

    def p_const_float(self, p):
        """const : FLOAT"""
        p[0] = AST.Float(p[1], p.lineno(1))

    def p_const_string(self, p):
        """const : STRING"""
        p[0] = AST.String([1], p.lineno(1))


    def p_const_expression(self, p):
        """expression : const"""
        p[0] = AST.Const(p[1], p.lineno(1))


    def p_expression_id(self, p):
        """expression : ID"""
        p[0] = AST.Variable(p[1], p.lineno(1))


    def p_pare_expression(self, p):
        """expression : '(' expression ')'
                      | '(' error ')'"""
        p[0] = AST.PareExpr(p[2])


    def p_id_pare_expression(self, p):
        """expression : ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        p[0] = AST.IDPareExpr(p[1], p[3], p.lineno(1))


    def p_expression(self, p):
        """expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression
                      | expression '|' expression
                      | expression '&' expression
                      | expression '^' expression
                      | expression AND expression
                      | expression OR expression
                      | expression SHL expression
                      | expression SHR expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression '>' expression
                      | expression '<' expression
                      | expression LE expression
                      | expression GE expression"""
        p[0] = AST.BinExpr(p[2], p[1], p[3], p.lineno(1))


    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        p[0] = None if len(p) == 1 else p[1]


    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        if len(p) == 2:
            p[0] = AST.ExprList()
            p[0].add(p[1])
        else:
            p[0] = AST.ExprList() if p[1] is None else p[1]
            p[0].add(p[3])


    def p_fundefs_opt(self, p):
        """fundefs_opt : fundefs
                       | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = AST.FunDefs()

    def p_fundefs(self, p):
        """fundefs : fundefs fundef
                   | fundef """
        if len(p) == 2:
            p[0] = AST.FunDefs()
            p[0].add(p[1])
        else:
            p[0] = AST.FunDefs() if p[1] is None else p[1]
            p[0].add(p[2])


    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr """

        p[0] = AST.FunDef(p[1], p[2], p[4], p[6])


    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        p[0] = None if len(p) == 1 else p[1]

    def p_args_list(self, p):
        """args_list : args_list ',' arg
                     | arg """
        if len(p) == 2:
            p[0] = AST.ArgsList()
            p[0].add(p[1])
        else:
            p[0] = AST.ArgsList() if p[1] is None else p[1]
            p[0].add(p[3])

    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = AST.Arg(p[1], p[2], p.lineno(1))


