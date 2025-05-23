import java.math.BigInteger;
import java.util.ArrayList;

public class Poly {
    private ArrayList<Mono> monoList;
    
    public Poly(ArrayList<Mono> monoList) {
        this.monoList = monoList;
    }
    
    public Poly addPoly(Poly p) {
        for (Mono m : p.getMonoList()) {
            int flag = 0;
            for (Mono mono : this.monoList) {
                if (mono.isAddable(m)) {
                    mono.setCoe(mono.getCoe().add(m.getCoe()));
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                monoList.add(m);
            }
        }
        return this;
    }
    
    public Poly mulPoly(Poly p) {
        ArrayList<Mono> result = new ArrayList<Mono>();
        Poly poly = new Poly(result);
        for (Mono m : p.getMonoList()) {
            for (Mono mono : this.monoList) {
                BigInteger coeff = m.getCoe().multiply(mono.getCoe());
                BigInteger varExp = m.getVarExp().add(mono.getVarExp());
                ArrayList<Sin> sinList1 = m.getSinList();
                ArrayList<Sin> sinList2 = mono.getSinList();
                ArrayList<Cos> cosList1 = m.getCosList();
                ArrayList<Cos> cosList2 = mono.getCosList();
                for (Sin sin1 : sinList1) {
                    int flag = 0;
                    for (Sin sin2 : sinList2) {
                        Poly poly1 = sin1.getPoly();
                        Poly poly2 = sin2.getPoly();
                        if (poly1.equals(poly2)) {
                            sin2.setExp(sin1.getExp().add(sin2.getExp()));
                            flag = 1;
                            break;
                        }
                    }
                    if (flag == 0) {
                        sinList2.add(sin1);
                    }
                }
                for (Cos cos1 : cosList1) {
                    int flag = 0;
                    for (Cos cos2 : cosList2) {
                        Poly poly1 = cos1.getPoly();
                        Poly poly2 = cos2.getPoly();
                        if (poly1.equals(poly2)) {
                            cos2.setExp(cos1.getExp().add(cos2.getExp()));
                            flag = 1;
                            break;
                        }
                    }
                    if (flag == 0) {
                        cosList2.add(cos1);
                    }
                }
                Mono newMono = new Mono(coeff, varExp,sinList2,cosList2);
                ArrayList<Mono> temp = new ArrayList<Mono>();
                temp.add(newMono);
                Poly tempPoly = new Poly(temp);
                poly = poly.addPoly(tempPoly);
            }
        }
        return poly;
    }
    
    public Poly powPoly(BigInteger exp) {
        if (exp.compareTo(BigInteger.ZERO) == 0) {
            ArrayList<Mono> monoList = new ArrayList<Mono>();
            monoList.add(new Mono(new BigInteger("1")
                , new BigInteger("0"), new ArrayList<Sin>(), new ArrayList<Cos>()));
            return new Poly(monoList);
        } else if (exp.compareTo(BigInteger.ONE) == 0) {
            return this;
        } else {
            Poly temp = this.mulPoly(this);
            int exp1 = exp.intValue();
            for (int i = 2; i < exp1; i++) {
                temp = temp.mulPoly(this);
            }
            return temp;
        }
    }
    
    public void negate() {
        for (Mono mono : monoList) {
            mono.setCoe(mono.getCoe().negate());
        }
    }
    
    public ArrayList<Mono> getMonoList() {
        return monoList;
    }
    
    public boolean equals(Poly p) {
        ArrayList<Mono> monoList1 = this.getMonoList();
        ArrayList<Mono> monoList2 = p.getMonoList();
        if (monoList1.size() != monoList2.size()) {
            return false;
        }
        for (Mono mono1 : monoList1) {
            int flag = 0;
            for (Mono mono2 : monoList2) {
                if (mono1.equals(mono2)) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                return false;
            }
        }
        return true;
    }
    
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (Mono mono : monoList) {
            BigInteger coeff = mono.getCoe();
            if (coeff.compareTo(BigInteger.ZERO) < 0) {
                continue;
            }
            if (coeff.compareTo(BigInteger.ZERO) == 0) {
                sb.append("");
            } else {
                sb.append(mono.toString());
            }
        }
        for (Mono mono : monoList) {
            BigInteger coeff = mono.getCoe();
            if (coeff.compareTo(BigInteger.ZERO) > 0) {
                continue;
            }
            if (coeff.compareTo(BigInteger.ZERO) == 0) {
                sb.append("");
            } else {
                sb.append(mono.toString());
            }
        }
        if (sb.toString().isEmpty()) {
            sb.append("0");
        }
        return sb.toString();
    }
}
