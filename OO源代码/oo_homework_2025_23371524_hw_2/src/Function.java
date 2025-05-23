import java.util.ArrayList;

public class Function implements Factor {
    private String newFunc;
    private Expr expr;
    
    public Function(String name, int layer, ArrayList<String> actualParas) {
        this.newFunc = FunctionDefiner.callFunc(name,layer,actualParas);
        this.expr = setExpr();
    }
    
    private Expr setExpr() {
        String s = Preprocessing.process(newFunc);
        Lexer lexer = new Lexer(s);
        Parser parser = new Parser(lexer);
        return parser.parseExpr();
    }
    
    public Expr getExpr() {
        return this.expr;
    }
    
    public Poly toPoly() {
        return expr.toPoly();
    }
}
