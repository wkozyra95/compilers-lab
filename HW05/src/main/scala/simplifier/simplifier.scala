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
      case IfElseExpr(cond, left, _) if simplify(cond) == TrueConst()  =>
        simplify(left)
      case IfElseExpr(cond, _, right) if simplify(cond) == FalseConst() =>
        simplify(right)
      case `node` =>
        node
    }
  }

  def unarySimplifier(unary:Unary)= {
    val reverseCompareOperator = Map(
      "==" -> "!=",
      "!=" -> "==",
      "<=" -> ">",
      "<" -> ">=",
      ">=" -> "<",
      ">" -> "<="
    )

    (unary.op, simplify(unary.expr)) match {
        // not ( x > y) -> x <= y
      case ("not", BinExpr(op, left, right)) if reverseCompareOperator.contains(op) =>
        BinExpr(reverseCompareOperator(op), left, right)
      case ("-", Unary("-", node)) => node
        // - - x -> x
      case ("not", Unary("not", node)) => node
        // not not x -> x
      case ("not", TrueConst()) => FalseConst()
        // not false -> true
      case ("not", FalseConst()) => TrueConst()
      case (op, node) => Unary(op, node)
    }
  }


  def binExprSimplifier(expr:BinExpr):Node= {

    val rootBinarySimplifier = List(
      constantsEvaluator,
      binExprMinusesSimplifier,
      multiplicationSimplifier,
      divisionAndCommutativitySimplifier,
      concatenationSimplifier,
      powerSimplifier,

      // x + 0 -> x
      oneSpecialArgument("+")(zeroEquality, result = identity),
      // x + [] -> x
      oneSpecialArgument("+")(_ == ElemList(List()), result = identity),
      // x * 0 -> 0
      oneSpecialArgument("*")(zeroEquality, result = _ => IntNum(0)),
      // x * 1 -> x
      oneSpecialArgument("*")(oneEquality, result = identity),

      // x - x -> 0
      sameArguments("-")(_ => IntNum(0)),
      // x / x -> 1
      sameArguments("/")(_ =>IntNum(1)),
      // x or x -> x
      sameArguments("or")(identity),
      // x == x -> true
      sameArguments("==")(_ => TrueConst()),
      sameArguments("<=")(_ => TrueConst()),
      sameArguments(">=")(_ => TrueConst()),
      sameArguments("!=")(_ => FalseConst()),
      // x < x -> false
      sameArguments("<")(_ => FalseConst()),
      // x > x -> false
      sameArguments(">")(_ => FalseConst()),
      // x and x -> x
      sameArguments("and")(identity),

      // x and true  -> x
      oneSpecialArgument("and")(_ == TrueConst(), identity),
      // x and false -> false
      oneSpecialArgument("and")(_ == FalseConst(), _ => FalseConst()),
      // x or true -> true
      oneSpecialArgument("or")(_ == TrueConst(), _ => TrueConst()),
      // x or false -> x
      oneSpecialArgument("or")(_ == FalseConst(), identity)
    )

    val expr2 = BinExpr(expr.op, simplify(expr.left), simplify(expr.right))

    rootBinarySimplifier
      .find(_.isDefinedAt(expr2))
      .map(func => func(expr2))
      .getOrElse(expr2)
  }

  val powerSimplifier: PartialFunction[BinExpr, Node] = {
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

  val multiplicationSimplifier: PartialFunction[BinExpr, Node] = {
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

  val constantsEvaluator: PartialFunction[BinExpr, Node] = {
    case BinExpr(op, leftNum:FloatNum, rightNum:FloatNum) =>
      FloatNum(evalBinExprDouble(op, leftNum.value, rightNum.value))
    case BinExpr(op, leftNum:IntNum, rightNum:FloatNum) =>
      FloatNum(evalBinExprDouble(op, leftNum.value.toDouble, rightNum.value))
    case BinExpr(op, leftNum:FloatNum, rightNum:IntNum) =>
      FloatNum(evalBinExprDouble(op, leftNum.value, rightNum.value.toDouble))
    case BinExpr(op, leftNum:IntNum, rightNum:IntNum) =>
      IntNum(evalBinExprInt(op, leftNum.value, rightNum.value))
  }

  val divisionAndCommutativitySimplifier: PartialFunction[BinExpr, Node]= {
    // 1/(1/c) = c
    case BinExpr("/", a, BinExpr("/", b, c))
      if oneEquality(a) && oneEquality(b) => c
    // a*(1/c) = a/c
    case BinExpr("*", a, BinExpr("/", b, c))
      if oneEquality(b) => BinExpr("/", a, c)
    // (1/c)*a = a/c
    case BinExpr("*", BinExpr("/", b, c), a)
      if oneEquality(b) => BinExpr("/", a, c)
    // a+b-a = b
    case BinExpr("+", a, BinExpr("-", b, c))
      if a.customEquals(c) => b
    // b-a+a = b
    case BinExpr("+", BinExpr("-", b, c), a)
      if a.customEquals(c) => b
    // a-(a+c) = -c
    case BinExpr("-", a, BinExpr("+", b, c))
      if a.customEquals(b) => Unary("-", c)
    // a-(b+a) = -b
    case BinExpr("-", a, BinExpr("+", b, c))
      if a.customEquals(c) => Unary("-", b)
    // a+c-a = c
    case BinExpr("-", BinExpr("+", b, c), a)
      if a.customEquals(b) => c
    // b+a-a = b
    case BinExpr("-", BinExpr("+", b, c), a)
      if a.customEquals(c) => b
  }


  val binExprMinusesSimplifier: PartialFunction[BinExpr, Node] = {
    // -a+(-b) = -(a+b)
    case BinExpr("+", Unary("-", leftNode), Unary("-", rightNode))  =>
      Unary("-", BinExpr("+", leftNode, rightNode))
    // -a+b = b-a
    case BinExpr("+", Unary("-", leftNode), rightNode)  =>
      binExprSimplifier(BinExpr("-", rightNode, leftNode))
    // a+(-b) = a-b
    case BinExpr("+", leftNode, Unary("-", rightNode))  =>
      binExprSimplifier(BinExpr("-", leftNode, rightNode))
  }

  val concatenationSimplifier: PartialFunction[BinExpr, Node] = {
    case BinExpr("+", ElemList(list1), ElemList(list2))  =>
      ElemList(list1++list2)
    case BinExpr("+", Tuple(list1), Tuple(list2))  =>
      Tuple(list1++list2)
  }

  def sameArguments(op:String)(result:Node=>Node): PartialFunction[BinExpr, Node] = {
    case BinExpr(`op`, left, right) if left.customEquals(right) =>
      result(left)
  }

  def oneSpecialArgument(op:String)(condition:Node=>Boolean, result:Node=>Node): PartialFunction[BinExpr, Node] = {
    case BinExpr(`op`, left, right) if condition(left) =>
      result(right)
    case BinExpr(`op`, left, right) if condition(right) =>
      result(left)
  }

  def zeroEquality(node:Node)= {
    node match {
      case IntNum(0) => true
      case FloatNum(0.0) => true
      case _ => false
    }
  }

  def oneEquality(node:Node)= {
    node match {
      case IntNum(1) => true
      case FloatNum(1.0) => true
      case _ => false
    }
  }

  def evalBinExprInt(op:String, left:Int, right:Int):Int= {
    op match {
      case "**" => math.pow(left, right).toInt
      case "*" => left * right
      case "/" => left / right
      case "+" => left + right
      case "-" => left - right
    }
  }

  def evalBinExprDouble(op:String, left:Double, right:Double):Double= {
    op match {
      case "**" => math.pow(left, right)
      case "*" => left * right
      case "/" => left / right
      case "+" => left + right
      case "-" => left - right
    }
  }
}
