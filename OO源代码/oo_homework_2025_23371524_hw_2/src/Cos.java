import java.math.BigInteger;
import java.util.ArrayList;

public class Cos implements Factor {
    private BigInteger coe = new BigInteger("1");
    private BigInteger exp;
    private Factor inside;
    private Poly poly;
    
    public Cos(BigInteger exp, Factor inside) {
        this.exp = exp;
        this.inside = inside;
    }
    
    public Cos(BigInteger exp, Poly poly) {
        this.exp = exp;
        this.poly = poly;
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
    
    public boolean equals(Cos cos2) {
        if (this.exp.compareTo(cos2.getExp()) == 0 && this.poly.equals(cos2.getPoly())) {
            return true;
        } else {
            return false;
        }
    }
    
    public boolean isZero() {
        if (poly.toString().equals("0")) {
            return true;
        } else {
            return false;
        }
    }
    
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("cos(");
        if (poly.isSingle()) {
            sb.append(poly.toString());
        } else {
            sb.append("(");
            sb.append(poly.toString());
            sb.append(")");
        }
        sb.append(")");
        if (!this.exp.equals(BigInteger.ONE)) {
            sb.append("^");
            sb.append(exp.toString());
        }
        return sb.toString();
    }
    
    public Poly toPoly() {
        if (exp.compareTo(BigInteger.ZERO) == 0) {
            Mono mono = new Mono(BigInteger.ONE, BigInteger.ZERO,
                new ArrayList<Sin>(), new ArrayList<Cos>());
            ArrayList<Mono> monoList = new ArrayList<Mono>();
            monoList.add(mono);
            return new Poly(monoList);
        } else {
            this.poly = this.inside.toPoly();
            if (this.isZero()) {
                Mono mono = new Mono(BigInteger.ONE, BigInteger.ZERO,
                    new ArrayList<Sin>(), new ArrayList<Cos>());
                ArrayList<Mono> monoList = new ArrayList<Mono>();
                monoList.add(mono);
                return new Poly(monoList);
            }
            this.poly.check();
            ArrayList<Sin> sinList = new ArrayList<Sin>();
            ArrayList<Cos> cosList = new ArrayList<Cos>();
            cosList.add(this);
            Mono mono = new Mono(BigInteger.ONE, BigInteger.ZERO,sinList,cosList);
            ArrayList<Mono> monoList = new ArrayList<Mono>();
            monoList.add(mono);
            Poly poly = new Poly(monoList);
            return poly;
        }
    }
}
