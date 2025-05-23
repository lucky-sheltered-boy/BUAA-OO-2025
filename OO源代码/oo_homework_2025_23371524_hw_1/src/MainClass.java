import java.util.Scanner;

public class MainClass {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        input = Preprocessing.process(input);
        //System.out.println(input);
        Lexer lexer = new Lexer(input);
        Parser parser = new Parser(lexer);
        Expr expr = parser.parseExpr();
        Poly poly = expr.toPoly();
        String output = poly.toString();
        if (output.charAt(0) == '+') {
            output = output.substring(1);
        }
        System.out.print(output);
    }
}
