import com.oocourse.elevator1.TimableOutput;

public class MainClass {
    public static void main(String[] args) {
        TimableOutput.initStartTimestamp();
        long startTime = System.currentTimeMillis();
        Executer.execute(startTime);
    }
}
