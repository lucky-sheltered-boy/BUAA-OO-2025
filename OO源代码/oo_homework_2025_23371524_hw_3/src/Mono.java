import java.math.BigInteger;
import java.util.ArrayList;

public class Mono {
    private BigInteger coe;
    private BigInteger varExp;
    private ArrayList<Sin> sinList;
    private ArrayList<Cos> cosList;

    public Mono(BigInteger coe, BigInteger varExp, ArrayList<Sin> sinList, ArrayList<Cos> cosList) {
        this.coe = coe;
        this.varExp = varExp;
        this.sinList = sinList;
        this.cosList = cosList;
    }

    public BigInteger getCoe() {
        return coe;
    }

    public BigInteger getVarExp() {
        return varExp;
    }
    
    public ArrayList<Sin> getSinList() {
        return sinList;
    }
    
    public ArrayList<Cos> getCosList() {
        return cosList;
    }
    
    public void setCoe(BigInteger coe) {
        this.coe = coe;
    }

    public void setVarExp(BigInteger varExp) {
        this.varExp = varExp;
    }
    
    public boolean isAddable(Mono m) {
        if (this.varExp.compareTo(m.getVarExp()) != 0) {
            return false;
        } else if (this.sinList.size() != m.getSinList().size() ||
            this.cosList.size() != m.getCosList().size()) {
            return false;
        } else {
            ArrayList<Sin> sinList1 = this.sinList;
            ArrayList<Cos> cosList1 = this.cosList;
            ArrayList<Sin> sinList2 = m.getSinList();
            ArrayList<Cos> cosList2 = m.getCosList();
            int flag1 = 1;
            for (Sin sin1 : sinList1) {
                int flag = 0;
                for (Sin sin2: sinList2) {
                    if (sin1.equals(sin2)) {
                        flag = 1;
                        break;
                    }
                }
                if (flag == 0) {
                    flag1 = 0;
                    break;
                }
            }
            if (flag1 == 0) {
                return false;
            }
            for (Cos cos1 : cosList1) {
                int flag = 0;
                for (Cos cos2: cosList2) {
                    if (cos1.equals(cos2)) {
                        flag = 1;
                        break;
                    }
                }
                if (flag == 0) {
                    flag1 = 0;
                    break;
                }
            }
            if (flag1 == 0) {
                return false;
            }
            return true;
        }
    }
    
    public boolean equals(Mono mono2) {
        if (this.coe.compareTo(mono2.getCoe()) == 0 && this.isAddable(mono2)) {
            return true;
        } else {
            return false;
        }
    }
    
    public boolean canBeSimplified(Mono mono2) {
        if (this.getVarExp().compareTo(mono2.getVarExp()) != 0 ||
            this.sinList.isEmpty() && this.cosList.isEmpty() ||
            mono2.sinList.isEmpty() && mono2.cosList.isEmpty()) {
            return false;
        }
        Mono mutual = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        Mono differ1 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        Mono differ2 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        classify(mono2, mutual, differ1, differ2);
        return elsePartt(differ1, differ2);
    }
    
    public boolean elsePartt(Mono differ1, Mono differ2) {
        if (differ1.getSinList().size() == 1 && differ1.getCosList().isEmpty()
            && differ2.getSinList().isEmpty() && differ2.getCosList().size() == 1) {
            Sin sin = differ1.getSinList().get(0);
            Cos cos = differ2.getCosList().get(0);
            if (sin.getExp().compareTo(new BigInteger("2")) == 0
                && cos.getExp().compareTo(new BigInteger("2")) == 0
                && sin.getPoly().equals(cos.getPoly())) {
                return true;
            } else {
                return false;
            }
        } else if (differ1.getCosList().size() == 1 && differ1.getSinList().isEmpty()
            && differ2.getCosList().isEmpty() && differ2.getSinList().size() == 1) {
            Cos cos = differ1.getCosList().get(0);
            Sin sin = differ2.getSinList().get(0);
            if (cos.getExp().compareTo(new BigInteger("2")) == 0
                && sin.getExp().compareTo(new BigInteger("2")) == 0
                && cos.getPoly().equals(sin.getPoly())) {
                return true;
            } else {
                return false;
            }
        } else {
            return false;
        }
    }
    
    public boolean canBeSimplified2(Mono mono2) {
        if (this.getVarExp().compareTo(mono2.getVarExp()) != 0 ||
            this.sinList.isEmpty() && this.cosList.isEmpty() ||
            mono2.sinList.isEmpty() && mono2.cosList.isEmpty() ||
            this.coe.abs().compareTo(mono2.getCoe().abs()) != 0) {
            return false;
        }
        Mono mutual = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        Mono differ1 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        Mono differ2 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        classify(mono2, mutual, differ1, differ2);
        return elsePartt2(differ1, differ2);
    }
    
    public boolean elsePartt2(Mono differ1, Mono differ2) {
        if (differ1.getSinList().size() == 1 && differ1.getCosList().size() == 1 &&
            differ2.getSinList().size() == 1 && differ2.getCosList().size() == 1) {
            Sin sin1 = differ1.getSinList().get(0);
            Cos cos1 = differ1.getCosList().get(0);
            Sin sin2 = differ2.getSinList().get(0);
            Cos cos2 = differ2.getCosList().get(0);
            if (sin1.getExp().compareTo(new BigInteger("1")) == 0 &&
                cos1.getExp().compareTo(new BigInteger("1")) == 0 &&
                sin2.getExp().compareTo(new BigInteger("1")) == 0 &&
                cos2.getExp().compareTo(new BigInteger("1")) == 0) {
                if (sin1.getPoly().equals(cos2.getPoly()) &&
                    cos1.getPoly().equals(sin2.getPoly())) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } else {
            return false;
        }
    }
    
    public void classify(Mono mono2, Mono mutual, Mono differ1, Mono differ2) {
        for (Sin sin1 : this.sinList) {
            int flag = 0;
            for (Sin sin2 : mono2.sinList) {
                if (sin1.equals(sin2)) {
                    mutual.sinList.add(sin1);
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ1.sinList.add(sin1);
            }
        }
        for (Cos cos1 : this.cosList) {
            int flag = 0;
            for (Cos cos2 : mono2.cosList) {
                if (cos1.equals(cos2)) {
                    mutual.cosList.add(cos1);
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ1.cosList.add(cos1);
            }
        }
        for (Sin sin2 : mono2.sinList) {
            int flag = 0;
            for (Sin sin1 : this.sinList) {
                if (sin2.equals(sin1)) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ2.sinList.add(sin2);
            }
        }
        for (Cos cos2 : mono2.cosList) {
            int flag = 0;
            for (Cos cos1 : this.cosList) {
                if (cos2.equals(cos1)) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ2.cosList.add(cos2);
            }
        }
    }
    
    public Poly dx() {
        ArrayList<Mono> temp = new ArrayList<>();
        Poly poly = new Poly(temp);
        poly = processVar(poly);
        poly = processSin(poly);
        poly = processCos(poly);
        return poly;
    }
    
    public Poly processVar(Poly poly1) {
        if (this.varExp.compareTo(BigInteger.ZERO) == 0) {
            return poly1;
        } else {
            Mono mono = this.clone();
            mono.setCoe(mono.getCoe().multiply(mono.getVarExp()));
            mono.setVarExp(mono.getVarExp().subtract(BigInteger.ONE));
            ArrayList<Mono> temp = new ArrayList<>();
            temp.add(mono);
            Poly poly2 = new Poly(temp);
            Poly poly = poly1;
            poly = poly.addPoly(poly2);
            return poly;
        }
    }
    
    public Poly processSin(Poly poly1) {
        Mono mono1 = this.clone();
        Poly poly = poly1;
        for (Sin sin : mono1.sinList) {
            Mono mono = mono1.removeSin(sin);
            ArrayList<Mono> temp = new ArrayList<>();
            temp.add(mono);
            Poly other = new Poly(temp);
            Poly derive = sin.dx();
            poly = poly.addPoly(other.mulPoly(derive));
        }
        return poly;
    }
    
    public Mono removeSin(Sin sin) {
        Mono mono = this.clone();
        for (Sin sin2 : mono.sinList) {
            if (sin2.equals(sin)) {
                mono.sinList.remove(sin2);
                break;
            }
        }
        return mono;
    }
    
    public Poly processCos(Poly poly1) {
        Mono mono1 = this.clone();
        Poly poly = poly1;
        for (Cos cos : mono1.cosList) {
            Mono mono = mono1.removeCos(cos);
            ArrayList<Mono> temp = new ArrayList<>();
            temp.add(mono);
            Poly other = new Poly(temp);
            Poly derive = cos.dx();
            poly = poly.addPoly(other.mulPoly(derive));
        }
        return poly;
    }
    
    public Mono removeCos(Cos cos) {
        Mono mono = this.clone();
        for (Cos cos2 : mono.cosList) {
            if (cos2.equals(cos)) {
                mono.cosList.remove(cos2);
                break;
            }
        }
        return mono;
    }
    
    public Mono clone() {
        Mono mono = new Mono(this.coe, this.varExp, new ArrayList<Sin>(), new ArrayList<Cos>());
        for (Sin sin : this.sinList) {
            mono.sinList.add(sin.clone());
        }
        for (Cos cos : this.cosList) {
            mono.cosList.add(cos.clone());
        }
        return mono;
    }
    
    public String toString() {
        StringBuilder sb = new StringBuilder();
        int flag2 = 0;
        for (Sin sin : sinList) {
            if (sin.isZero() && sin.getExp().compareTo(BigInteger.ZERO) != 0) {
                flag2 = 1;
                break;
            }
        }
        if (this.coe.compareTo(BigInteger.ZERO) == 0 || flag2 == 1) {
            sb.append("");
        } else {
            if (varExp.compareTo(BigInteger.ZERO) == 0 &&
                sinList.isEmpty() && cosList.isEmpty()) {
                if (coe.compareTo(BigInteger.ZERO) > 0) {
                    sb.append("+");
                }
                sb.append(coe);
            } else {
                sb = elsePart(sb);
            }
        }
        return sb.toString();
    }
    
    public StringBuilder elsePart(StringBuilder sb2) {
        StringBuilder sb = sb2;
        if (varExp.compareTo(BigInteger.ZERO) == 0) {
            if (coe.compareTo(BigInteger.ONE) == 0
                || coe.compareTo(new BigInteger("-1")) == 0) {
                if (coe.compareTo(BigInteger.ONE) == 0) {
                    sb.append("+");
                } else {
                    sb.append("-");
                }
                int flag = 1;
                for (Sin sin : sinList) {
                    if (flag == 1) {
                        sb.append(sin.toString());
                        flag = 0;
                    } else {
                        sb.append("*" + sin.toString());
                    }
                }
                for (Cos cos : cosList) {
                    if (flag == 1) {
                        sb.append(cos.toString());
                        flag = 0;
                    } else {
                        sb.append("*" + cos.toString());
                    }
                }
                if (sb.length() == 1) {
                    sb.append("1");
                }
            } else {
                if (coe.compareTo(BigInteger.ZERO) > 0) {
                    sb.append("+");
                }
                sb.append(coe);
                for (Sin sin : sinList) {
                    sb.append("*").append(sin.toString());
                }
                for (Cos cos : cosList) {
                    sb.append("*").append(cos.toString());
                }
            }
        } else {
            sb = elsePart2(sb);
        }
        return sb;
    }
    
    public StringBuilder elsePart2(StringBuilder sb) {
        if (coe.compareTo(BigInteger.ONE) == 0) {
            sb.append("+x");
        } else if (coe.compareTo(new BigInteger("-1")) == 0) {
            sb.append("-x");
        } else {
            if (coe.compareTo(BigInteger.ZERO) > 0) {
                sb.append("+");
            }
            sb.append(coe + "*x");
        }
        if (varExp.compareTo(BigInteger.ONE) == 0) {
            sb.append("");
        } else {
            sb.append("^" + varExp);
        }
        if (!this.sinList.isEmpty()) {
            for (Sin sin : sinList) {
                sb.append("*" + sin.toString());
            }
        }
        if (!this.cosList.isEmpty()) {
            for (Cos cos : cosList) {
                sb.append("*" + cos.toString());
            }
        }
        return sb;
    }
}
