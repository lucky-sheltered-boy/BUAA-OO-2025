import com.oocourse.elevator2.TimableOutput;

public class MainClass {
    public static void main(String[] args) {
        TimableOutput.initStartTimestamp();
        long startTime = System.currentTimeMillis();
        Executor.execute(startTime);
    }
}
