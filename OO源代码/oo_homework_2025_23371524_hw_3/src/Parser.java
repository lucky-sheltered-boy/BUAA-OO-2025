import java.math.BigInteger;
import java.util.ArrayList;

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
        } else if (token.getType() == Token.Type.LPAREN) {
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
        } else if (token.getType() == Token.Type.DX) {
            return parseDx();
        } else {
            return parseFunc();
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
        return new Cos(exp,inside);
    }
    
    public Function parseFunc() {
        Token token = lexer.getCurToken();
        final String name = token.getContent();
        int layer;
        if (name.equals("f")) {
            lexer.nextToken();
            lexer.nextToken();
            layer = Integer.parseInt(lexer.getCurToken().getContent());
            lexer.nextToken();
            lexer.nextToken();
            lexer.nextToken();
        } else {
            lexer.nextToken();
            lexer.nextToken();
            layer = 0;
        }
        ArrayList<String> factors = new ArrayList<String>();
        Factor factor1 = parseFactor();
        factors.add(factor1.toPoly().toString());
        if (lexer.getCurToken().getType() == Token.Type.COMMA) {
            lexer.nextToken();
            Factor factor2 = parseFactor();
            factors.add(factor2.toPoly().toString());
        }
        lexer.nextToken();
        return new Function(name, layer, factors);
    }
    
    public Dx parseDx() {
        lexer.nextToken();
        lexer.nextToken();
        Expr expr = parseExpr();
        lexer.nextToken();
        return new Dx(expr);
    }
}
