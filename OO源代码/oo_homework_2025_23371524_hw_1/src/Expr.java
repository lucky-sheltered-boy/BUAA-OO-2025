import java.math.BigInteger;
import java.util.ArrayList;

public class Expr implements Factor {
    private final ArrayList<Term> terms = new ArrayList<>();
    private BigInteger exp = BigInteger.ONE;
    
    public void addTerm(Term term) {
        terms.add(term);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("(");
        for (Term term : terms) {
            sb.append(term.toString());
        }
        sb.append(")^" + exp);
        return sb.toString();
    }

    public void print() {
        System.out.println("Expr " + this);
    }
    
    public void setExp(BigInteger exp) {
        this.exp = exp;
    }
    
    public BigInteger getExp() {
        return exp;
    }
    
    public Poly toPoly() {
        ArrayList<Mono> monos = new ArrayList<>();
        Poly poly = new Poly(monos);
        for (Term term : terms) {
            poly = poly.addPoly(term.toPoly());
        }
        poly = poly.powPoly(exp);
        return poly;
    }
}
