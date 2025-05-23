import java.util.ArrayList;
import java.util.Scanner;

public class MainClass {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        scanner.nextLine();
        for (int i = 0; i < n; i++) {
            ArrayList<String> list = new ArrayList<String>();
            for (int j = 0; j < 3; j++) {
                list.add(scanner.nextLine());
            }
            FunctionDefiner.addFunc(list);
        }
        String input = scanner.nextLine();
        input = Preprocessing.process(input);
        Lexer lexer = new Lexer(input);
        Parser parser = new Parser(lexer);
        Expr expr = parser.parseExpr();
        Poly poly = expr.toPoly();
        poly = poly.addItself();
        String output = poly.toString();
        System.out.print(output);
    }
}
