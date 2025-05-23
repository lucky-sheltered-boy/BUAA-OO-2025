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
        this.sinList = new ArrayList<Sin>();
        this.cosList = new ArrayList<Cos>();
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
    
    public String toString() {
        StringBuilder sb = new StringBuilder();
        if (this.coe.compareTo(BigInteger.ZERO) == 0) {
            sb.append("");
        } else if (varExp.compareTo(BigInteger.ZERO) == 0) {
            if (coe.compareTo(BigInteger.ZERO) > 0) {
                sb.append("+");
            }
            sb.append(coe);
        } else {
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
        }
        if (this.sinList.size() > 0) {
            for (Sin sin : sinList) {
                sb.append("*" + sin.toString());
            }
        }
        if (this.cosList.size() > 0) {
            for (Cos cos : cosList) {
                sb.append("*" + cos.toString());
            }
        }
        return sb.toString();
    }
}
