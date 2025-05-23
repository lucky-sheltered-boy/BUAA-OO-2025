import java.math.BigInteger;
import java.util.ArrayList;

public class Num implements Factor {
    private final BigInteger value;

    public Num(String value) {
        this.value = new BigInteger(value);
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }

    public void print() {
        System.out.println("Num " + this);
    }
    
    public BigInteger getValue() {
        return value;
    }
    
    public Poly toPoly() {
        Mono mono = new Mono(value, BigInteger.ZERO,new ArrayList<Sin>(),new ArrayList<Cos>());
        ArrayList<Mono> monos = new ArrayList<Mono>();
        monos.add(mono);
        return new Poly(monos);
    }
}
