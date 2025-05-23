import java.util.ArrayList;

public class Lexer {
    private final ArrayList<Token> tokens = new ArrayList<>();
    private int index = 0;

    public Lexer(String input) {
        int pos = 0;
        while (pos < input.length()) {
            if (input.charAt(pos) == '(') {
                tokens.add(new Token(Token.Type.LPAREN, "("));
                pos++;
            } else if (input.charAt(pos) == ')') {
                tokens.add(new Token(Token.Type.RPAREN, ")"));
                pos++;
            } else if (input.charAt(pos) == '+') {
                tokens.add(new Token(Token.Type.ADD, "+"));
                pos++;
            } else if (input.charAt(pos) == '-') {
                tokens.add(new Token(Token.Type.SUB, "-"));
                pos++;
            } else if (input.charAt(pos) == '*') {
                tokens.add(new Token(Token.Type.MUL, "*"));
                pos++;
            } else if (input.charAt(pos) == 'x') {
                tokens.add(new Token(Token.Type.VAR, "x"));
                pos++;
            } else if (input.charAt(pos) == 's') {
                tokens.add(new Token(Token.Type.SIN,"sin"));
                pos += 3;
            } else if (input.charAt(pos) == 'c') {
                tokens.add(new Token(Token.Type.COS, "cos"));
                pos += 3;
            } else if (input.charAt(pos) == '^') {
                tokens.add(new Token(Token.Type.EXP, "^"));
                pos++;
            } else if (input.charAt(pos) == '{') {
                tokens.add(new Token(Token.Type.LBRACE, "{"));
                pos++;
            } else if (input.charAt(pos) == '}') {
                tokens.add(new Token(Token.Type.RBRACE, "}"));
                pos++;
            } else if (input.charAt(pos) == ',') {
                tokens.add(new Token(Token.Type.COMMA, ","));
                pos++;
            } else if (input.charAt(pos) >= '0' && input.charAt(pos) <= '9') {
                char now = input.charAt(pos);
                StringBuilder sb = new StringBuilder();
                while (now >= '0' && now <= '9') {
                    sb.append(now);
                    pos++;
                    if (pos >= input.length()) {
                        break;
                    }
                    now = input.charAt(pos);
                }
                tokens.add(new Token(Token.Type.NUM, sb.toString()));
            } else {
                tokens.add(new Token(Token.Type.FUNCNAME, String.valueOf(input.charAt(pos))));
                pos++;
            }
        }
    }

    public Token getCurToken() {
        return tokens.get(index);
    }

    public void nextToken() {
        index++;
    }

    public boolean isEnd() {
        return index >= tokens.size();
    }
    
    public ArrayList<Token> getTokens() {
        return tokens;
    }
}
