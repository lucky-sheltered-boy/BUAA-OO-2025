import com.oocourse.elevator3.TimableOutput;

public class MainClass {
    public static void main(String[] args) {
        TimableOutput.initStartTimestamp();
        long startTime = System.currentTimeMillis();
        Executor.execute(startTime);
    }
}
