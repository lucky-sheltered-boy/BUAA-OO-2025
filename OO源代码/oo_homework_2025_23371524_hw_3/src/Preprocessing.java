public class Preprocessing {
    public static String process(String input) {
        String temp = processSpace(input);
        return processOperator(temp);
    }
    
    public static String processSpace(String input) {
        StringBuilder sb = new StringBuilder();
        int length = input.length();
        for (int i = 0; i < length; i++) {
            char c = input.charAt(i);
            if (c != ' ' && c != '\t') {
                sb.append(c);
            }
        }
        return sb.toString();
    }
    
    public static String processOperator(String input) {
        StringBuilder sb = new StringBuilder();
        int length = input.length();
        for (int i = 0; i < length; i++) {
            char c = input.charAt(i);
            if (i + 1 < length) {
                char c1 = input.charAt(i + 1);
                if (isOperator(c) && isOperator(c1)) {
                    if (c == '+' && c1 == '+' || c == '-' && c1 == '-') {
                        sb.append("+");
                        i++;
                    } else if (c == '+' && c1 == '-' || c == '-' && c1 == '+') {
                        sb.append("-");
                        i++;
                    }
                } else {
                    sb.append(c);
                }
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
    
    public static boolean isOperator(char c) {
        return c == '+' || c == '-';
    }
}
