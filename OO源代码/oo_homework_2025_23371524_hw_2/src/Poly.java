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
                this.monoList.add(m);
            }
        }
        return this;
    }
    
    public Poly mulPoly(Poly p) {
        ArrayList<Mono> result = new ArrayList<Mono>();
        Poly poly = new Poly(result);
        for (Mono m : p.getMonoList()) {
            for (Mono mono : this.monoList) {
                final BigInteger coeff = m.getCoe().multiply(mono.getCoe());
                final BigInteger varExp = m.getVarExp().add(mono.getVarExp());
                ArrayList<Sin> sinList1 = m.getSinList();
                ArrayList<Sin> sinList2T = mono.getSinList();
                ArrayList<Sin> sinList2 = new ArrayList<Sin>();
                ArrayList<Cos> cosList2 = new ArrayList<Cos>();
                for (Sin sin2 : sinList2T) {
                    Sin newSin = new Sin(sin2.getExp(), sin2.getPoly());
                    sinList2.add(newSin);
                }
                ArrayList<Cos> cosList1 = m.getCosList();
                ArrayList<Cos> cosList2T = mono.getCosList();
                for (Cos cos2 : cosList2T) {
                    Cos newCos = new Cos(cos2.getExp(), cos2.getPoly());
                    cosList2.add(newCos);
                }
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
        for (Mono mono : this.monoList) {
            mono.setCoe(mono.getCoe().negate());
        }
    }
    
    public boolean check() {
        ArrayList<Mono> monoList = this.getMonoList();
        if (monoList.isEmpty()) {
            return false;
        }
        BigInteger max = monoList.get(0).getVarExp();
        Mono temp = monoList.get(0);
        for (Mono mono : monoList) {
            if (mono.getVarExp().compareTo(max) > 0) {
                max = mono.getVarExp();
                temp = mono;
            } else if (mono.getVarExp().compareTo(max) == 0 &&
                mono.getSinList().size() + mono.getCosList().size() >
                temp.getSinList().size() + temp.getCosList().size()) {
                max = mono.getVarExp();
                temp = mono;
            }
        }
        if (temp.getCoe().compareTo(BigInteger.ZERO) < 0) {
            this.negate();
            return true;
        } else {
            return false;
        }
    }
    
    public ArrayList<Mono> getMonoList() {
        return monoList;
    }
    
    public void setMonoList(ArrayList<Mono> monoList) {
        this.monoList = monoList;
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
    
    public boolean isSingle() {
        if (monoList.size() != 1) {
            return false;
        }
        Mono mono = monoList.get(0);
        BigInteger coeff = mono.getCoe();
        BigInteger varExp = mono.getVarExp();
        ArrayList<Sin> sinList = mono.getSinList();
        ArrayList<Cos> cosList = mono.getCosList();
        if (varExp.compareTo(BigInteger.ZERO) == 0 && sinList.isEmpty() && cosList.isEmpty()) {
            return true;
        }
        if (coeff.compareTo(BigInteger.ONE) == 0 && varExp.compareTo(BigInteger.ZERO) != 0
            && sinList.isEmpty() && cosList.isEmpty()) {
            return true;
        }
        if (coeff.compareTo(BigInteger.ONE) == 0 && varExp.compareTo(BigInteger.ZERO) == 0
            && sinList.size() == 1 && cosList.isEmpty()) {
            return true;
        }
        if (coeff.compareTo(BigInteger.ONE) == 0 && varExp.compareTo(BigInteger.ZERO) == 0
            && sinList.isEmpty() && cosList.size() == 1) {
            return true;
        }
        return false;
    }
    
    public Poly addItself() {
        Poly result = new Poly(new ArrayList<Mono>());
        for (Mono mono : this.getMonoList()) {
            ArrayList<Mono> temp = new ArrayList<Mono>();
            temp.add(mono);
            Poly tempPoly = new Poly(temp);
            result = result.addPoly(tempPoly);
        }
        return result;
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
        String output = sb.toString();
        if (output.charAt(0) == '+') {
            output = output.substring(1);
        }
        return output;
    }
}
