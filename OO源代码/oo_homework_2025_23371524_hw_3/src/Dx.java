public class Dx implements Factor {
    private Expr expr;
    private Poly poly;
    
    public Dx(Expr expr) {
        this.expr = expr;
        Poly temp = this.expr.toPoly();
        this.poly = temp.dx();
    }
    
    public Poly toPoly() {
        return poly;
    }
}
