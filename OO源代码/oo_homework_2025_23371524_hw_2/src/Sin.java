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
    
    public Sin(BigInteger exp, Poly poly) {
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
    
    public boolean isZero() {
        if (poly.toString().equals("0")) {
            return true;
        } else {
            return false;
        }
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
                Mono mono = new Mono(BigInteger.ZERO, BigInteger.ZERO,
                    new ArrayList<Sin>(), new ArrayList<Cos>());
                ArrayList<Mono> monoList = new ArrayList<Mono>();
                monoList.add(mono);
                return new Poly(monoList);
            }
            ArrayList<Sin> sinList = new ArrayList<Sin>();
            ArrayList<Cos> cosList = new ArrayList<Cos>();
            if (this.poly.check()) {
                sinList.add(this);
                if (BigInteger.ZERO.compareTo((this.exp.mod(new BigInteger("2")))) == 0) {
                    Mono mono = new Mono(new BigInteger("1"), BigInteger.ZERO,sinList,cosList);
                    ArrayList<Mono> monoList = new ArrayList<Mono>();
                    monoList.add(mono);
                    Poly poly = new Poly(monoList);
                    return poly;
                } else {
                    Mono mono = new Mono(new BigInteger("-1"), BigInteger.ZERO,sinList,cosList);
                    ArrayList<Mono> monoList = new ArrayList<Mono>();
                    monoList.add(mono);
                    Poly poly = new Poly(monoList);
                    return poly;
                }
            } else {
                sinList.add(this);
                Mono mono = new Mono(BigInteger.ONE, BigInteger.ZERO,sinList,cosList);
                ArrayList<Mono> monoList = new ArrayList<Mono>();
                monoList.add(mono);
                Poly poly = new Poly(monoList);
                return poly;
            }
        }
    }
}
