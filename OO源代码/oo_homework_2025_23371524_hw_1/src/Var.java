import java.math.BigInteger;
import java.util.ArrayList;

public class Var implements Factor {
    private final String name;
    private BigInteger exp;
    
    public Var(String name, BigInteger exp) {
        this.name = name;
        this.exp = exp;
    }

    @Override
    public String toString() {
        return name + "^" + exp;
    }

    public void print() {
        System.out.println("Var " + this);
    }
    
    public String getName() {
        return name;
    }
    
    public BigInteger getExp() {
        return exp;
    }
    
    public Poly toPoly() {
        BigInteger coe = new BigInteger("1");
        Mono mono = new Mono(coe,this.exp, new ArrayList<Sin>(), new ArrayList<Cos>());
        ArrayList<Mono> monos = new ArrayList<Mono>();
        monos.add(mono);
        return new Poly(monos);
    }
}
