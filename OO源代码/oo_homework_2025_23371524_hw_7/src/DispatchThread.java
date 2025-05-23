import com.oocourse.elevator3.TimableOutput;

import java.util.HashMap;

public class DispatchThread extends Thread {
    private RequestTable requestTable;
    private HashMap<Integer, ElevatorTable> elevatorTableMap;
    private DispatchStrategy dispatchStrategy;

    public DispatchThread(RequestTable requestTable, HashMap<Integer,
        ElevatorTable> elevatorTableMap) {
        this.requestTable = requestTable;
        this.elevatorTableMap = elevatorTableMap;
        this.dispatchStrategy = new DispatchStrategy(requestTable, elevatorTableMap);
    }

    @Override
    public void run() {
        while (true) {
            if (!dispatchStrategy.dispatch()) {
                if (requestTable.isOver()) {
                    for (ElevatorTable elevatorTable : elevatorTableMap.values()) {
                        elevatorTable.setEndFlag();
                        if (Debug.debug()) {
                            TimableOutput.println("[LOG] elevator-" +
                                elevatorTable.getElevatorId() + "-setEnd");
                        }
                    }
                    break;
                }
                if (Debug.debug()) {
                    TimableOutput.println("[LOG] dispatcher-" + "failed to dispatch-sleep 50ms");
                }
                try {
                    sleep(50);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
