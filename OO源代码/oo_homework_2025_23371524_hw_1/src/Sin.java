import java.math.BigInteger;
import java.util.ArrayList;

public class Sin implements Factor {
    private BigInteger coe = new BigInteger("1");
    private BigInteger exp;
    private Factor inside;
    private Poly poly;
    
    public Sin(BigInteger exp, Factor inside) {
        this.exp = exp;
        this.inside = inside;
    }
    
    public BigInteger getExp() {
        return exp;
    }
    
    public void setExp(BigInteger exp) {
        this.exp = exp;
    }
    
    public Factor getInside() {
        return inside;
    }
    
    public Poly getPoly() {
        return poly;
    }
    
    public boolean equals(Sin sin2) {
        if (this.exp.compareTo(sin2.getExp()) == 0 && this.poly.equals(sin2.getPoly())) {
            return true;
        } else {
            return false;
        }
    }
    
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("sin(");
        sb.append(inside.toString());
        sb.append(")");
        if (!this.exp.equals(BigInteger.ONE)) {
            sb.append("^");
            sb.append(exp.toString());
        }
        return sb.toString();
    }
    
    public Poly toPoly() {
        ArrayList<Sin> sinList = new ArrayList<Sin>();
        ArrayList<Cos> cosList = new ArrayList<Cos>();
        this.poly = this.inside.toPoly();
        sinList.add(this);
        Mono mono = new Mono(BigInteger.ONE, BigInteger.ZERO,sinList,cosList);
        ArrayList<Mono> monoList = new ArrayList<Mono>();
        monoList.add(mono);
        Poly poly = new Poly(monoList);
        return poly;
    }
}
