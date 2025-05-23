import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;

public class FunctionDefiner {
    private static HashMap<String, ArrayList<String>> funcMap = new HashMap<>();
    private static HashMap<String, ArrayList<String>> paraMap = new HashMap<>();
    
    public static void addFunc(ArrayList<String> s1) {
        ArrayList<String> func = new ArrayList<>();
        ArrayList<String> s = preProcess(s1);
        String name = getFuncName(s);
        funcMap.put(name, func);
        String str0 = getString(s, '0');
        ArrayList<String> para = getFuncPara(str0);
        paraMap.put(name, para);
        
        funcMap.get(name).add(getFuncBody(str0));
        String str1 = getString(s, '1');
        funcMap.get(name).add(getFuncBody(str1));
        
        String strn = getString(s, 'n');
        ArrayList<BigInteger> coe = new ArrayList<>();
        ArrayList<String> para1 = new ArrayList<>();
        ArrayList<String> para2 = new ArrayList<>();
        String lastExpr = parseFuncn(strn, coe, para1, para2);
        for (int n = 2; n <= 5; n++) {
            String ori = "";
            ori += coe.get(0).toString();
            ori += "*";
            ori += "(";
            ori += callFunc(name,n - 1,para1);
            ori += ")";
            ori += "+";
            ori += coe.get(1).toString();
            ori += "*";
            ori += "(";
            ori += callFunc(name,n - 2,para2);
            ori += ")";
            ori += lastExpr;
            funcMap.get(name).add(ori);
        }
        ArrayList<String> original = funcMap.get(name);
        for (String line : original) {
            //System.out.println(line);
        }
    }
    
    public static String callFunc(String name,int layer,ArrayList<String> actualParas) {
        String original = funcMap.get(name).get(layer);
        StringBuilder sb = new StringBuilder();
        int length = original.length();
        ArrayList<String> para = paraMap.get(name);
        HashMap<String, String> paraMap = new HashMap<>();
        for (int i = 0; i < para.size(); i++) {
            paraMap.put(para.get(i), actualParas.get(i));
        }
        for (int i = 0; i < length; i++) {
            if (para.contains(String.valueOf(original.charAt(i)))) {
                sb.append('(');
                sb.append(paraMap.get(String.valueOf(original.charAt(i))));
                sb.append(')');
            } else {
                sb.append(original.charAt(i));
            }
        }
        return sb.toString();
    }
    
    public static ArrayList<String> preProcess(ArrayList<String> code) {
        ArrayList<String> code1 = new ArrayList<>();
        for (String line : code) {
            code1.add(Preprocessing.process(line));
        }
        return code1;
    }
    
    public static String getString(ArrayList<String> code, char c) {
        for (String line : code) {
            int index = line.indexOf('{') + 1;
            if (line.charAt(index) == c) {
                return line;
            }
        }
        return null;
    }
    
    public static String getFuncName(ArrayList<String> code) {
        return String.valueOf(code.get(0).charAt(0));
    }
    
    public static ArrayList<String> getFuncPara(String s) {
        ArrayList<String> para = new ArrayList<>();
        int length = s.length();
        int start = s.indexOf('(') + 1;
        for (int i = start; i < length; i++) {
            if (s.charAt(i) == 'x' || s.charAt(i) == 'y') {
                para.add(String.valueOf(s.charAt(i)));
            }
            if (s.charAt(i) == ')') {
                break;
            }
        }
        return para;
    }
    
    public static String getFuncBody(String s) {
        int start = s.indexOf('=') + 1;
        return s.substring(start);
    }
    
    public static String parseFuncn(String strn, ArrayList<BigInteger> coe,
        ArrayList<String> para1, ArrayList<String> para2) {
        int start = strn.indexOf('=') + 1;
        StringBuilder sbcoe1 = new StringBuilder();
        if (strn.charAt(start) == '+' || strn.charAt(start) == '-') {
            sbcoe1.append(strn.charAt(start));
            start++;
        }
        while (start < strn.length() && strn.charAt(start)  >= '0' && strn.charAt(start)  <= '9') {
            sbcoe1.append(strn.charAt(start));
            start++;
        }
        if (sbcoe1.length() == 0) {
            sbcoe1.append("1");
        }
        coe.add(new BigInteger(sbcoe1.toString()));
        while (strn.charAt(start) != '(') {
            start++;
        }
        int stack = 0;
        stack++;
        start++;
        StringBuilder sbpara11 = new StringBuilder();
        while (start < strn.length() && strn.charAt(start) != ',') {
            if (strn.charAt(start) == '(') {
                stack++;
            }
            if (strn.charAt(start) == ')') {
                stack--;
                if (stack == 0) {
                    break;
                }
            }
            sbpara11.append(strn.charAt(start));
            start++;
        }
        para1.add(sbpara11.toString());
        if (strn.charAt(start) == ',') {
            start++;
            stack = 1;
            StringBuilder sbpara12 = new StringBuilder();
            while (start < strn.length() && strn.charAt(start) != ',') {
                if (strn.charAt(start) == '(') {
                    stack++;
                }
                if (strn.charAt(start) == ')') {
                    stack--;
                    if (stack == 0) {
                        break;
                    }
                }
                sbpara12.append(strn.charAt(start));
                start++;
            }
            para1.add(sbpara12.toString());
        }
        start++;
        return parseFuncn2(strn, coe, para1, para2, start);
    }
    
    public static String parseFuncn2(String strn, ArrayList<BigInteger> coe,
        ArrayList<String> para1, ArrayList<String> para2, int start2) {
        int start = start2;
        StringBuilder sbcoe2 = new StringBuilder();
        if (strn.charAt(start) == '+' || strn.charAt(start) == '-') {
            sbcoe2.append(strn.charAt(start));
            start++;
        }
        while (start < strn.length() && strn.charAt(start)  >= '0' && strn.charAt(start)  <= '9') {
            sbcoe2.append(strn.charAt(start));
            start++;
        }
        if (sbcoe2.length() == 0) {
            sbcoe2.append("1");
        }
        coe.add(new BigInteger(sbcoe2.toString()));
        while (strn.charAt(start) != '(') {
            start++;
        }
        int stack = 0;
        stack++;
        start++;
        StringBuilder sbpara21 = new StringBuilder();
        while (start < strn.length() && strn.charAt(start) != ',') {
            if (strn.charAt(start) == '(') {
                stack++;
            }
            if (strn.charAt(start) == ')') {
                stack--;
                if (stack == 0) {
                    break;
                }
            }
            sbpara21.append(strn.charAt(start));
            start++;
        }
        para2.add(sbpara21.toString());
        if (strn.charAt(start) == ',') {
            start++;
            stack = 1;
            StringBuilder sbpara22 = new StringBuilder();
            while (start < strn.length() && strn.charAt(start) != ',') {
                if (strn.charAt(start) == '(') {
                    stack++;
                }
                if (strn.charAt(start) == ')') {
                    stack--;
                    if (stack == 0) {
                        break;
                    }
                }
                sbpara22.append(strn.charAt(start));
                start++;
            }
            para2.add(sbpara22.toString());
        }
        start++;
        return strn.substring(start);
    }
}
