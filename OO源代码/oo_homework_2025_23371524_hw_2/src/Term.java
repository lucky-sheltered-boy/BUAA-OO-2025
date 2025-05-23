import java.util.ArrayList;
import java.math.BigInteger;

public class Term {
    private final ArrayList<Factor> factors = new ArrayList<>();
    private char sign;
    
    public Term(char sign) {
        this.sign = sign;
    }
    
    public void addFactor(Factor factor) {
        factors.add(factor);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(sign);
        for (Factor factor : factors) {
            if (factor instanceof Expr) {
                sb.append("(" + factor.toString() + ")");
            } else {
                sb.append(factor.toString());
            }
            sb.append("*");
        }
        return sb.substring(0, sb.length() - 1); // remove the last "*"
    }

    public void print() {
        System.out.println("Term " + this);
    }
    
    public Poly toPoly() {
        BigInteger coe = new BigInteger("1");
        Mono mono = new Mono(coe,new BigInteger("0"),new ArrayList<Sin>(),new ArrayList<Cos>());
        ArrayList<Mono> monos = new ArrayList<>();
        monos.add(mono);
        Poly poly = new Poly(monos);
        for (Factor it : factors) {
            Poly temp = poly.mulPoly(it.toPoly());
            poly = temp;
        }
        if (sign == '-') {
            poly.negate();
            sign = '+';
        }
        return poly;
    }
}
