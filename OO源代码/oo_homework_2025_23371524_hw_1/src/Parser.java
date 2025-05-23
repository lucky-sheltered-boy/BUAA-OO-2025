import java.math.BigInteger;

public class Parser {
    private final Lexer lexer;

    public Parser(Lexer lexer) {
        this.lexer = lexer;
    }

    public Expr parseExpr() {
        Expr expr = new Expr();
        char sign = '+';
        if (lexer.getCurToken().getType() == Token.Type.SUB) {
            sign = '-';
            lexer.nextToken();
        } else if (lexer.getCurToken().getType() == Token.Type.ADD) {
            lexer.nextToken();
        }
        expr.addTerm(parseTerm(sign));
        while (!lexer.isEnd() && (lexer.getCurToken().getType() == Token.Type.ADD
            || lexer.getCurToken().getType() == Token.Type.SUB)) {
            if (lexer.getCurToken().getType() == Token.Type.ADD) {
                lexer.nextToken();
                expr.addTerm(parseTerm('+'));
            } else if (lexer.getCurToken().getType() == Token.Type.SUB) {
                lexer.nextToken();
                expr.addTerm(parseTerm('-'));
            }
        }
        return expr;
    }

    public Term parseTerm(char sign) {
        Term term = new Term(sign);
        term.addFactor(parseFactor());
        while (!lexer.isEnd() && lexer.getCurToken().getType() == Token.Type.MUL) {
            lexer.nextToken();
            term.addFactor(parseFactor());
        }
        //term.print();
        return term;
    }

    public Factor parseFactor() {
        Token token = lexer.getCurToken();
        if (token.getType() == Token.Type.NUM || token.getType() == Token.Type.SUB
            || token.getType() == Token.Type.ADD) {
            return parseNum();
        } else if (token.getType() == Token.Type.VAR) {
            return parseVar();
        } else if (token.getType() == Token.Type.SIN) {
            return parseSin();
        } else if (token.getType() == Token.Type.COS) {
            return parseCos();
        } else {
            lexer.nextToken();
            Expr subExpression = parseExpr();
            lexer.nextToken();
            BigInteger exp = new BigInteger("1");
            if (!lexer.isEnd() && lexer.getCurToken().getType() == Token.Type.EXP) {
                lexer.nextToken();
                if (lexer.getCurToken().getType() == Token.Type.ADD) {
                    lexer.nextToken();
                    exp = new BigInteger(lexer.getCurToken().getContent());
                    lexer.nextToken();
                } else {
                    exp = new BigInteger(lexer.getCurToken().getContent());
                    lexer.nextToken();
                }
            }
            subExpression.setExp(exp);
            //subExpression.print();
            return subExpression;
        }
    }

    public Num parseNum() {
        Num num;
        Token token = lexer.getCurToken();
        String number;
        char sign = '+';
        if (token.getType() == Token.Type.SUB || token.getType() == Token.Type.ADD) {
            if (token.getType() == Token.Type.SUB) {
                sign = '-';
            }
            lexer.nextToken();
            token = lexer.getCurToken();
            number = sign + token.getContent();
        } else {
            number = token.getContent();
        }
        lexer.nextToken();
        num = new Num(number);
        //num.print();
        return num;
    }

    public Var parseVar() {
        Token token = lexer.getCurToken();
        String name = token.getContent();
        lexer.nextToken();
        BigInteger exp = BigInteger.ONE;
        if (!lexer.isEnd() && lexer.getCurToken().getType() == Token.Type.EXP) {
            lexer.nextToken();
            if (lexer.getCurToken().getType() == Token.Type.ADD) {
                lexer.nextToken();
                exp = new BigInteger(lexer.getCurToken().getContent());
            } else {
                exp = new BigInteger(lexer.getCurToken().getContent());
            }
            lexer.nextToken();
        }
        Var var = new Var(name, exp);
        //var.print();
        return var;
    }
    
    public Sin parseSin() {
        lexer.nextToken();
        lexer.nextToken();
        Factor inside = parseFactor();
        lexer.nextToken();
        BigInteger exp = BigInteger.ONE;
        if (!lexer.isEnd() && lexer.getCurToken().getType() == Token.Type.EXP) {
            lexer.nextToken();
            if (lexer.getCurToken().getType() == Token.Type.ADD) {
                lexer.nextToken();
                exp = new BigInteger(lexer.getCurToken().getContent());
            } else {
                exp = new BigInteger(lexer.getCurToken().getContent());
            }
            lexer.nextToken();
        }
        //System.out.println("sin(" + inside.toString() + ")^" + exp.toString());
        return new Sin(exp,inside);
    }
    
    public Cos parseCos() {
        lexer.nextToken();
        lexer.nextToken();
        Factor inside = parseFactor();
        lexer.nextToken();
        BigInteger exp = BigInteger.ONE;
        if (!lexer.isEnd() && lexer.getCurToken().getType() == Token.Type.EXP) {
            lexer.nextToken();
            if (lexer.getCurToken().getType() == Token.Type.ADD) {
                lexer.nextToken();
                exp = new BigInteger(lexer.getCurToken().getContent());
            } else {
                exp = new BigInteger(lexer.getCurToken().getContent());
            }
            lexer.nextToken();
        }
        //System.out.println("cos(" + inside.toString() + ")^" + exp.toString());
        return new Cos(exp,inside);
    }
}
