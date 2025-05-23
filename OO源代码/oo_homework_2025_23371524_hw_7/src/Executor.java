import java.util.HashMap;

public class Executor {
    public static void execute(long startTime) {
        RequestTable requestTable = new RequestTable();
        new InputThread(requestTable).start();
        HashMap<Integer, ElevatorTable> elevatorMap = new HashMap<>();
        for (int i = 1; i <= 6; i++) {
            ElevatorTable elevatorTable = new ElevatorTable(i, 6, true, startTime);
            elevatorMap.put(i, elevatorTable);
            ElevatorThread elevatorThread = new ElevatorThread(i, elevatorTable, requestTable);
            elevatorThread.start();
        }
        new DispatchThread(requestTable, elevatorMap).start();
    }
}
