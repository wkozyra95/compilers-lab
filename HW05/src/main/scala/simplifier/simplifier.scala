package simplifier

import AST._

// to implement
// avoid one huge match of cases
// take into account non-greedy strategies to resolve cases with power laws
object Simplifier {

  def simplify(node: Node): Node = {
    node match {
      case NodeList(list) =>
        val newList = list.map(simplify).filter(_ != EmptyNode)

        val pairs = newList.dropRight(1).zip(newList.drop(1))
        val assignmentsToDelete = pairs.collect{
          case (x @ Assignment(var1, expr1), Assignment(var2, expr2)) if var1 == var2 =>
            x
        }

        newList.diff(assignmentsToDelete) match {
          case List() =>
            EmptyNode
          case List(NodeList(nestedList))=>
            NodeList(nestedList)
          case justList =>
            NodeList(justList)
        }

      case expr:BinExpr=>
        binExprSimplifier(expr)
      case unary:Unary=>
        unarySimplifier(unary)

      case Assignment(a, b) if a == simplify(b) =>
        EmptyNode
      case Assignment(a, b) =>
        Assignment(a, simplify(b))
      case WhileInstr(cond, body) if simplify(cond) == FalseConst() =>
        EmptyNode
      case KeyDatumList(list)=>
        KeyDatumList(list.groupBy(_.key).map{case(key, values)=>values.last}.toList)
      case IfElseInstr(cond, left, _) if simplify(cond) == TrueConst()  =>
        simplify(left)
      case IfElseInstr(cond, _, right) if simplify(cond) == FalseConst() =>
        simplify(right)
      case e @ IfElseExpr(cond, left, _) if simplify(cond) == TrueConst()  =>
        simplify(left)
      case IfElseExpr(cond, _, right) if simplify(cond) == FalseConst() =>
        simplify(right)
      case `node` =>
        node
    }
  }

  def unarySimplifier(unary:Unary)={
    val comparisonPairs = Map(
      "==" -> "!=",
      "!=" -> "==",
      "<=" -> ">",
      "<" -> ">=",
      ">=" -> "<",
      ">" -> "<="
    )

    (unary.op, simplify(unary.expr)) match {
      case ("not", BinExpr(op, left, right)) if comparisonPairs.contains(op) =>
        BinExpr(comparisonPairs(op), left, right)
      case ("-", Unary("-", node)) => node
      case ("not", Unary("not", node)) => node
      case ("not", TrueConst()) => FalseConst()
      case ("not", FalseConst()) => TrueConst()
      case (op, node) => Unary(op, node)
    }
  }


  def binExprSimplifier(expr:BinExpr):Node={
    def always[A, B](x:B):A=>B = _ => x

    val simplifiers = List(
      conditionForOne("+")(condition = isZero, result = identity),
      conditionForOne("+")(condition = _ == ElemList(List()), result = identity),
      conditionForOne("*")(condition = isZero, result = always(IntNum(0))),
      conditionForOne("*")(condition = isOne, result = identity),
      ifSameArguments("-")(result =  always(IntNum(0))),
      ifSameArguments("/")(result =  always(IntNum(1))),
      ifSameArguments("or")(result = identity),
      ifSameArguments("==")(result = always(TrueConst())),
      ifSameArguments("<=")(result = always(TrueConst())),
      ifSameArguments(">=")(result = always(TrueConst())),
      ifSameArguments("!=")(result = always(FalseConst())),
      ifSameArguments("<")(result = always(FalseConst())),
      ifSameArguments(">")(result = always(FalseConst())),
      ifSameArguments("and")(result = identity),
      conditionForOne("and")(condition = _ == TrueConst(), result =  identity),
      conditionForOne("and")(condition = _ == FalseConst(), result = always(FalseConst())),
      conditionForOne("or")(condition = _ == TrueConst(), result = always(TrueConst())),
      conditionForOne("or")(condition = _ == FalseConst(), result = identity),
      constantsEvaluator,
      BinExprMinusesSimplifier,
      multiplicationSimplifier,
      divisionAndCommutativitySimplifier,
      concatenationSimplifier,
      powerSimplifier
    )

    val expr2 = BinExpr(expr.op, simplify(expr.left), simplify(expr.right))

    simplifiers
      .find(_.isDefinedAt(expr2))
      .map(func => func(expr2))
      .getOrElse(expr2)
  }

  val powerSimplifier: PartialFunction[BinExpr, Node] ={
    // a^b * a^d = a^(b+d)
    case BinExpr("*", BinExpr("**", a, b), BinExpr("**", c, d)) if a.customEquals(c)=>
      binExprSimplifier(BinExpr("**", a, BinExpr("+", b, d)))
    // a^0 = 1
    case BinExpr("**", a, IntNum(0)) => IntNum(1)
    // a^1 = a
    case BinExpr("**", a, IntNum(1)) => a
    // a^b^c = a^(b*c)
    case BinExpr("**", BinExpr("**", a, b), c) => BinExpr("**", a, BinExpr("*", b, c))
    // a^2 + 2ac + c^2 = (a+c)^2
    case BinExpr("+",
          BinExpr("+",
            BinExpr("**", a, IntNum(2)),
            BinExpr("*", BinExpr("*", IntNum(2), b), c)
            ),
            BinExpr("**", d, IntNum(2))
            )
      if a.customEquals(b) && c.customEquals(d) => BinExpr("**", BinExpr("+", a, c), IntNum(2))
    // (a+b)^2 - a^2 -2ba = b^2
    case BinExpr("-",
          BinExpr("-",
            BinExpr("**", BinExpr("+", a, b), IntNum(2)),
            BinExpr("**", c, IntNum(2))
            ),
          BinExpr("*", BinExpr("*", IntNum(2), d), e)
          )
      if a.customEquals(c) && c.customEquals(d) && b.customEquals(e)=> BinExpr("**", b, IntNum(2))
    // (a+b)^2 - (c-a)^2 = 4ab
    case BinExpr("-",
          BinExpr("**", BinExpr("+", a, b), IntNum(2)),
          BinExpr("**", BinExpr("-", c, d), IntNum(2))
          )
      if a.customEquals(c) && b.customEquals(d) => BinExpr("*", BinExpr("*", IntNum(4), a), b)
  }

  val multiplicationSimplifier: PartialFunction[BinExpr, Node] ={
    // ab - a = a*(b-1)
    case BinExpr("-", BinExpr("*", a, b), c)
      if a.customEquals(c) =>  binExprSimplifier(BinExpr("*", a, BinExpr("-", b, IntNum(1))))
    // a - ab = a*(1-b)
    case BinExpr("-", c, BinExpr("*", a, b))
      if a.customEquals(c) => binExprSimplifier(BinExpr("*", a, BinExpr("-", IntNum(1), b)))
    // ba - a = a*(b-1)
    case BinExpr("-", BinExpr("*", b, a), c)
      if a.customEquals(c) =>  binExprSimplifier(BinExpr("*", a, BinExpr("-", b, IntNum(1))))
    // a - ba = a*(1-b)
    case BinExpr("-", c, BinExpr("*", b, a))
      if a.customEquals(c) => binExprSimplifier(BinExpr("*", a, BinExpr("-", IntNum(1), b)))
    // ab + ad = a*(b+d)
    case BinExpr("+", BinExpr("*", a, b), BinExpr("*", c, d))
      if a.customEquals(c) =>  binExprSimplifier(BinExpr("*", a, BinExpr("+", b, d)))
    // ab + ca = a*(b+c)
    case BinExpr("+", BinExpr("*", a, b), BinExpr("*", c, d))
      if a.customEquals(d) => binExprSimplifier(BinExpr("*", a, BinExpr("+", b, c)))
    // ab + bd = (a+d)*b
    case BinExpr("+", BinExpr("*", a, b), BinExpr("*", c, d))
      if b.customEquals(c) => binExprSimplifier(BinExpr("*", BinExpr("+", a, d), b))
    // ab + cb = (a+c)*b
    case BinExpr("+", BinExpr("*", a, b), BinExpr("*", c, d))
      if b.customEquals(d) => binExprSimplifier(BinExpr("*", BinExpr("+", a, c), b))
    // a*(b+c) + db + dc = (a+d)*(b+c)
    case BinExpr("+",
          BinExpr("+",  BinExpr("*", a, BinExpr("+", b, c)),  BinExpr("*", d, e)),
          BinExpr("*", f, g)
          )
      if b.customEquals(e) && c.customEquals(g) && d.customEquals(f) =>
        BinExpr("*",  BinExpr("+",  a,  d),  BinExpr("+",  b,  c))

  }

  val constantsEvaluator: PartialFunction[BinExpr, Node] ={
    case BinExpr(op, leftNum:FloatNum, rightNum:FloatNum)=>
      FloatNum(executeDoubleBinExpr(op, leftNum.value, rightNum.value))
    case BinExpr(op, leftNum:IntNum, rightNum:FloatNum)=>
      FloatNum(executeDoubleBinExpr(op, leftNum.value.toDouble, rightNum.value))
    case BinExpr(op, leftNum:FloatNum, rightNum:IntNum)=>
      FloatNum(executeDoubleBinExpr(op, leftNum.value, rightNum.value.toDouble))
    case BinExpr(op, leftNum:IntNum, rightNum:IntNum)=>
      IntNum(executeIntBinExpr(op, leftNum.value, rightNum.value))
  }

  val divisionAndCommutativitySimplifier: PartialFunction[BinExpr, Node]={
    case BinExpr("/", a, BinExpr("/", b, c)) if isOne(a) && isOne(b) => c
    case BinExpr("/", BinExpr("/", b, c), a) if isOne(a) && isOne(b) => c

    case BinExpr("*", a, BinExpr("/", b, c)) if isOne(b) && isOne(b) => BinExpr("/", a, c)
    case BinExpr("*", BinExpr("/", b, c), a) if isOne(b) && isOne(b) => BinExpr("/", a, c)

    case BinExpr("+", a, BinExpr("-", b, c)) if a.customEquals(c) => b
    case BinExpr("+", BinExpr("-", b, c), a) if a.customEquals(c) => b

    case BinExpr("-", a, BinExpr("+", b, c)) if a.customEquals(b) => Unary("-", c)
    case BinExpr("-", a, BinExpr("+", b, c)) if a.customEquals(c) => Unary("-", b)

    case BinExpr("-", BinExpr("+", b, c), a) if a.customEquals(b) => c
    case BinExpr("-", BinExpr("+", b, c), a) if a.customEquals(c) => b
  }


  val BinExprMinusesSimplifier: PartialFunction[BinExpr, Node] ={
    case BinExpr("+", Unary("-", leftNode), Unary("-", rightNode))  =>
      Unary("-", BinExpr("+", leftNode, rightNode))

    case BinExpr("+", Unary("-", leftNode), rightNode)  =>
      binExprSimplifier(BinExpr("-", rightNode, leftNode))

    case BinExpr("+", leftNode, Unary("-", rightNode))  =>
      binExprSimplifier(BinExpr("-", leftNode, rightNode))
  }

  val concatenationSimplifier: PartialFunction[BinExpr, Node] ={
    case BinExpr("+", ElemList(list1), ElemList(list2))  =>
      ElemList(list1++list2)
    case BinExpr("+", Tuple(list1), Tuple(list2))  =>
      Tuple(list1++list2)
  }

  def ifSameArguments(op:String)(result:Node=>Node): PartialFunction[BinExpr, Node] ={
    case BinExpr(`op`, left, right) if left.customEquals(right) =>
      result(left)
  }

  def conditionForOne(op:String)(condition:Node=>Boolean, result:Node=>Node): PartialFunction[BinExpr, Node] ={
    case BinExpr(`op`, left, right) if condition(left) =>
      result(right)
    case BinExpr(`op`, left, right) if condition(right) =>
      result(left)
  }

  def isZero(node:Node)={
    node match {
      case IntNum(0) => true
      case FloatNum(0.0) => true
      case _ => false
    }
  }

  def isOne(node:Node)={
    node match {
      case IntNum(1) => true
      case FloatNum(1.0) => true
      case _ => false
    }
  }

  def executeIntBinExpr(op:String, left:Int, right:Int):Int={
    op match {
      case "**" => math.pow(left, right).toInt
      case "*" => left * right
      case "/" => left / right
      case "+" => left + right
      case "-" => left - right
    }
  }

  def executeDoubleBinExpr(op:String, left:Double, right:Double):Double={
    op match {
      case "**" => math.pow(left, right)
      case "*" => left * right
      case "/" => left / right
      case "+" => left + right
      case "-" => left - right
    }
  }
}
