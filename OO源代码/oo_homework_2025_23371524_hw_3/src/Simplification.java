import java.math.BigInteger;
import java.util.ArrayList;

public class Simplification {
    public static Poly simplify(Poly p) {
        int flag = 1;
        ArrayList<Mono> monoList = p.getMonoList();
        while (flag == 1) {
            flag = 0;
            int size = monoList.size();
            for (int i = 0; i < size; i++) {
                for (int j = i + 1; j < size; j++) {
                    if (monoList.get(i).canBeSimplified(monoList.get(j))) {
                        monoList = execute(monoList, i, j);
                        flag = 1;
                        break;
                    }
                }
                if (flag == 1) {
                    break;
                }
            }
        }
        Poly poly = new Poly(monoList);
        return poly;
    }
    
    public static ArrayList<Mono> execute(ArrayList<Mono> monoList1, int i, int j) {
        ArrayList<Mono> monoList = monoList1;
        Mono mono1 = monoList.get(i);
        Mono mono2 = monoList.get(j);
        Mono mutual = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        Mono differ1 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        mutual.setVarExp(mono1.getVarExp());
        Mono differ2 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        classify(mono1, mono2, mutual, differ1, differ2);
        BigInteger coef1 = mono1.getCoe();
        BigInteger coef2 = mono2.getCoe();
        ArrayList<Mono> mutualList = null;
        mutualList = checkStyle(coef1, coef2, mutual, differ1, differ2, mutualList, mono1, mono2);
        monoList.remove(mono1);
        monoList.remove(mono2);
        monoList.addAll(mutualList);
        return monoList;
    }
    
    public static Poly simplify2(Poly p) {
        int flag = 1;
        ArrayList<Mono> monoList = p.getMonoList();
        while (flag == 1) {
            flag = 0;
            int size = monoList.size();
            for (int i = 0; i < size; i++) {
                for (int j = i + 1; j < size; j++) {
                    if (monoList.get(i).canBeSimplified2(monoList.get(j))) {
                        monoList = execute2(monoList, i, j);
                        flag = 1;
                        break;
                    }
                }
                if (flag == 1) {
                    break;
                }
            }
        }
        Poly poly = new Poly(monoList);
        return poly;
    }
    
    public static ArrayList<Mono> execute2(ArrayList<Mono> monoList1, int i, int j) {
        ArrayList<Mono> monoList = monoList1;
        Mono mono1 = monoList.get(i);
        Mono mono2 = monoList.get(j);
        Mono mutual = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        Mono differ1 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        Mono differ2 = new Mono(BigInteger.ONE, BigInteger.ZERO,
            new ArrayList<>(), new ArrayList<>());
        classify(mono1, mono2, mutual, differ1, differ2);
        mutual.setVarExp(mono1.getVarExp());
        BigInteger coef1 = mono1.getCoe();
        BigInteger coef2 = mono2.getCoe();
        if (coef1.compareTo(coef2) == 0) {
            return do1(coef1, coef2, differ1, differ2, mono1, mono2, mutual, monoList);
        } else {
            return do2(coef1, coef2, differ1, differ2, mono1, mono2, mutual, monoList);
        }
    }
    
    public static ArrayList<Mono> do1(BigInteger coef1, BigInteger coef2, Mono differ1,
        Mono differ2, Mono mono1, Mono mono2, Mono mutual, ArrayList<Mono> monoList) {
        mutual.setCoe(mono1.getCoe());
        ArrayList<Mono> mutualList = null;
        mutualList = checkStyle2(mutual, differ1, differ2, mutualList, mono1, mono2);
        monoList.remove(mono1);
        monoList.remove(mono2);
        monoList.addAll(mutualList);
        return monoList;
    }
    
    public static ArrayList<Mono> do2(BigInteger coef1, BigInteger coef2, Mono differ1,
        Mono differ2, Mono mono1, Mono mono2, Mono mutual, ArrayList<Mono> monoList) {
        mutual.setCoe(coef1.abs());
        ArrayList<Mono> mutualList = null;
        mutualList = checkStyle3(mutual, differ1, differ2, mutualList, mono1, mono2);
        monoList.remove(mono1);
        monoList.remove(mono2);
        monoList.addAll(mutualList);
        return monoList;
    }
    
    public static void classify(Mono mono1, Mono mono2, Mono mutual, Mono differ1, Mono differ2) {
        for (Sin sin1 : mono1.getSinList()) {
            int flag = 0;
            for (Sin sin2 : mono2.getSinList()) {
                if (sin1.equals(sin2)) {
                    mutual.getSinList().add(sin1);
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ1.getSinList().add(sin1);
            }
        }
        for (Cos cos1 : mono1.getCosList()) {
            int flag = 0;
            for (Cos cos2 : mono2.getCosList()) {
                if (cos1.equals(cos2)) {
                    mutual.getCosList().add(cos1);
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ1.getCosList().add(cos1);
            }
        }
        for (Sin sin2 : mono2.getSinList()) {
            int flag = 0;
            for (Sin sin1 : mono1.getSinList()) {
                if (sin2.equals(sin1)) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ2.getSinList().add(sin2);
            }
        }
        for (Cos cos2 : mono2.getCosList()) {
            int flag = 0;
            for (Cos cos1 : mono1.getCosList()) {
                if (cos2.equals(cos1)) {
                    flag = 1;
                    break;
                }
            }
            if (flag == 0) {
                differ2.getCosList().add(cos2);
            }
        }
    }
    
    public static ArrayList<Mono> checkStyle(BigInteger coef1, BigInteger coef2,
        Mono mutual, Mono differ1, Mono differ2,
        ArrayList<Mono> mutualList1, Mono mono1, Mono mono2) {
        ArrayList<Mono> mutualList = mutualList1;
        if (coef1.compareTo(coef2) == 0) {
            mutual.setCoe(coef1);
            mutualList = new ArrayList<Mono>();
            mutualList.add(mutual);
        } else {
            ArrayList<Mono> monoListMutual = new ArrayList<Mono>();
            monoListMutual.add(mutual);
            Poly polyMutual = new Poly(monoListMutual);
            int num = compareAbsMin(coef1, coef2);
            if (num == 1) {
                mutualList = if1(coef1, coef2, differ1, differ2, mono1, mono2, polyMutual);
            } else if (num == 2) {
                mutualList = if2(coef1, coef2, differ1, differ2, mono1, mono2, polyMutual);
            } else if (num == 0) {
                if (coef1.compareTo(BigInteger.ZERO) > 0) {
                    if (!differ1.getSinList().isEmpty()) {
                        Poly polyDen = getPolyDen(differ1, coef2);
                        polyMutual = polyMutual.mulPoly(polyDen);
                        mutualList = polyMutual.getMonoList();
                    } else if (!differ1.getCosList().isEmpty()) {
                        Poly polyDen = getPoly(differ1, coef1);
                        polyMutual = polyMutual.mulPoly(polyDen);
                        mutualList = polyMutual.getMonoList();
                    }
                } else if (coef2.compareTo(BigInteger.ZERO) > 0) {
                    if (!differ2.getSinList().isEmpty()) {
                        Poly polyDen = getPolyDen(differ2, coef1);
                        polyMutual = polyMutual.mulPoly(polyDen);
                        mutualList = polyMutual.getMonoList();
                    } else if (!differ2.getCosList().isEmpty()) {
                        Poly polyDen = getPoly(differ2, coef2);
                        polyMutual = polyMutual.mulPoly(polyDen);
                        mutualList = polyMutual.getMonoList();
                    }
                }
            }
        }
        return mutualList;
    }
    
    public static ArrayList<Mono> if1(BigInteger coef1, BigInteger coef2, Mono differ1,
        Mono differ2, Mono mono1, Mono mono2, Poly polyMutual1) {
        Poly polyMutual = polyMutual1;
        Mono monoNum = new Mono(coef1, BigInteger.ZERO,
            new ArrayList<Sin>(),new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        ArrayList<Mono> mutualList;
        if (!differ2.getSinList().isEmpty()) {
            Sin sin = differ2.getSinList().get(0);
            ArrayList<Sin> sinList = new ArrayList<Sin>();
            sinList.add(sin);
            BigInteger coef = coef2.subtract(coef1);
            Mono monoDen = new Mono(coef, BigInteger.ZERO, sinList, new ArrayList<Cos>());
            ArrayList<Mono> monoListDen = new ArrayList<Mono>();
            monoListDen.add(monoDen);
            Poly polyDen = new Poly(monoListDen);
            polyNum = polyNum.addPoly(polyDen);
            polyMutual = polyMutual.mulPoly(polyNum);
            mutualList = polyMutual.getMonoList();
        } else {
            Cos cos = differ2.getCosList().get(0);
            ArrayList<Cos> cosList = new ArrayList<Cos>();
            cosList.add(cos);
            BigInteger coef = coef2.subtract(coef1);
            Mono monoDen = new Mono(coef, BigInteger.ZERO, new ArrayList<Sin>(), cosList);
            ArrayList<Mono> monoListDen = new ArrayList<Mono>();
            monoListDen.add(monoDen);
            Poly polyDen = new Poly(monoListDen);
            polyNum = polyNum.addPoly(polyDen);
            polyMutual = polyMutual.mulPoly(polyNum);
            mutualList = polyMutual.getMonoList();
        }
        return mutualList;
    }
    
    public static ArrayList<Mono> if2(BigInteger coef1, BigInteger coef2, Mono differ1,
        Mono differ2, Mono mono1, Mono mono2, Poly polyMutual1) {
        Poly polyMutual = polyMutual1;
        Mono monoNum = new Mono(coef2, BigInteger.ZERO,
            new ArrayList<Sin>(),new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        ArrayList<Mono> mutualList;
        if (!differ1.getSinList().isEmpty()) {
            Sin sin = differ1.getSinList().get(0);
            ArrayList<Sin> sinList = new ArrayList<Sin>();
            sinList.add(sin);
            BigInteger coef = coef1.subtract(coef2);
            Mono monoDen = new Mono(coef, BigInteger.ZERO, sinList, new ArrayList<Cos>());
            ArrayList<Mono> monoListDen = new ArrayList<Mono>();
            monoListDen.add(monoDen);
            Poly polyDen = new Poly(monoListDen);
            polyNum = polyNum.addPoly(polyDen);
            polyMutual = polyMutual.mulPoly(polyNum);
            mutualList = polyMutual.getMonoList();
        } else {
            Cos cos = differ1.getCosList().get(0);
            ArrayList<Cos> cosList = new ArrayList<Cos>();
            cosList.add(cos);
            BigInteger coef = coef1.subtract(coef2);
            Mono monoDen = new Mono(coef, BigInteger.ZERO, new ArrayList<Sin>(), cosList);
            ArrayList<Mono> monoListDen = new ArrayList<Mono>();
            monoListDen.add(monoDen);
            Poly polyDen = new Poly(monoListDen);
            polyNum = polyNum.addPoly(polyDen);
            polyMutual = polyMutual.mulPoly(polyNum);
            mutualList = polyMutual.getMonoList();
        }
        return mutualList;
    }
    
    public static Poly getPoly(Mono differ1, BigInteger coef1) {
        Cos cos = differ1.getCosList().get(0);
        Poly inside = cos.getPoly();
        Mono monoNum = new Mono(new BigInteger("2"), BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        Poly polyInside = inside.mulPoly(polyNum);
        Cos cosnew = new Cos(BigInteger.ONE,polyInside);
        ArrayList<Cos> cosList = new ArrayList<Cos>();
        cosList.add(cosnew);
        Mono monoDen = new Mono(coef1, BigInteger.ZERO, new ArrayList<Sin>(), cosList);
        ArrayList<Mono> monoListDen = new ArrayList<Mono>();
        monoListDen.add(monoDen);
        Poly polyDen = new Poly(monoListDen);
        return polyDen;
    }
    
    public static Poly getPolyDen(Mono differ1, BigInteger coef2) {
        Sin sin = differ1.getSinList().get(0);
        Poly inside = sin.getPoly();
        Mono monoNum = new Mono(new BigInteger("2"), BigInteger.ZERO,
            new ArrayList<Sin>(), new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        Poly polyInside = inside.mulPoly(polyNum);
        Cos cosnew = new Cos(BigInteger.ONE,polyInside);
        ArrayList<Cos> cosList = new ArrayList<Cos>();
        cosList.add(cosnew);
        Mono monoDen = new Mono(coef2, BigInteger.ZERO, new ArrayList<Sin>(), cosList);
        ArrayList<Mono> monoListDen = new ArrayList<Mono>();
        monoListDen.add(monoDen);
        Poly polyDen = new Poly(monoListDen);
        return polyDen;
    }
    
    public static ArrayList<Mono> checkStyle2(Mono mutual, Mono differ1, Mono differ2,
        ArrayList<Mono> mutualList1, Mono mono1, Mono mono2) {
        ArrayList<Mono> monoListMutual = new ArrayList<Mono>();
        monoListMutual.add(mutual);
        Poly poly1 = differ1.getSinList().get(0).getPoly();
        Poly poly2 = differ1.getCosList().get(0).getPoly();
        poly1 = poly1.addPoly(poly2);
        Sin sin = new Sin(BigInteger.ONE,poly1);
        ArrayList<Sin> sinList = new ArrayList<Sin>();
        Poly polyMutual = new Poly(monoListMutual);
        sinList.add(sin);
        ArrayList<Mono> mutualList = mutualList1;
        Mono monoNum = new Mono(BigInteger.ONE, BigInteger.ZERO, sinList, new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        polyMutual = polyMutual.mulPoly(polyNum);
        mutualList = polyMutual.getMonoList();
        return mutualList;
    }
    
    public static ArrayList<Mono> checkStyle3(Mono mutual, Mono differ1, Mono differ2,
        ArrayList<Mono> mutualList1, Mono mono1, Mono mono2) {
        ArrayList<Mono> monoListMutual = new ArrayList<Mono>();
        monoListMutual.add(mutual);
        Poly poly1 = differ1.getSinList().get(0).getPoly();
        Poly poly2 = differ1.getCosList().get(0).getPoly();
        Mono negate = new Mono(new BigInteger("-1"),
            BigInteger.ZERO, new ArrayList<Sin>(), new ArrayList<Cos>());
        ArrayList<Mono> negateList = new ArrayList<Mono>();
        negateList.add(negate);
        Poly negatePoly = new Poly(negateList);
        if (mono1.getCoe().compareTo(BigInteger.ZERO) > 0) {
            poly2 = poly2.mulPoly(negatePoly);
            poly1 = poly1.addPoly(poly2);
        } else {
            poly1 = poly1.mulPoly(negatePoly);
            poly1 = poly1.addPoly(poly2);
        }
        poly1 = Simplification.removeZero(poly1);
        Sin sin = new Sin(BigInteger.ONE,poly1);
        ArrayList<Sin> sinList = new ArrayList<Sin>();
        Poly polyMutual = new Poly(monoListMutual);
        sinList.add(sin);
        ArrayList<Mono> mutualList = mutualList1;
        Mono monoNum = new Mono(BigInteger.ONE, BigInteger.ZERO, sinList, new ArrayList<Cos>());
        ArrayList<Mono> monoListNum = new ArrayList<Mono>();
        monoListNum.add(monoNum);
        Poly polyNum = new Poly(monoListNum);
        polyMutual = polyMutual.mulPoly(polyNum);
        mutualList = polyMutual.getMonoList();
        return mutualList;
    }
    
    public static int compareAbsMin(BigInteger coef1, BigInteger coef2) {
        if (coef1.abs().compareTo(coef2.abs()) < 0) {
            return 1;
        } else if (coef1.abs().compareTo(coef2.abs()) > 0) {
            return 2;
        } else if (coef1.abs().compareTo(coef2.abs()) == 0) {
            return 0;
        } else {
            return -1;
        }
    }
    
    public static Poly removeZero(Poly p) {
        ArrayList<Mono> mono2 = p.getMonoList();
        ArrayList<Mono> removeList = new ArrayList<>();
        for (Mono mono : mono2) {
            if (mono.getCoe().compareTo(BigInteger.ZERO) == 0) {
                removeList.add(mono);
            }
        }
        for (Mono mono : removeList) {
            mono2.remove(mono);
        }
        Poly poly = new Poly(mono2);
        return poly;
    }
}
