import java.util.HashMap;

public class Executer {
    public static void execute(long startTime) {
        RequestTable requestTable = new RequestTable();
        HashMap<Integer, ElevatorTable> elevatorMap = new HashMap<>();
        for (int i = 1; i <= 6; i++) {
            ElevatorTable elevatorTable = new ElevatorTable(i, 6, true);
            elevatorMap.put(i, elevatorTable);
            ElevatorThread elevatorThread = new ElevatorThread(i, startTime, elevatorTable);
            elevatorThread.start();
        }
        new InputThread(requestTable).start();
        new DispatchThread(requestTable, elevatorMap).start();
    }
}
