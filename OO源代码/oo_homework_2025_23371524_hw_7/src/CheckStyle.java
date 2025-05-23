import com.oocourse.elevator3.TimableOutput;

import java.util.ArrayList;
import java.util.HashMap;

public class CheckStyle {
    public static int nextFloor(ElevatorTable elevatorTable) {
        int currentFloor = elevatorTable.getCurrentFloor();
        if (elevatorTable.getDirection()) {
            if (currentFloor != elevatorTable.getTopFloor()) {
                return currentFloor + 1;
            } else {
                return currentFloor;
            }
        } else {
            if (currentFloor != elevatorTable.getBottomFloor()) {
                return currentFloor - 1;
            } else {
                return currentFloor;
            }
        }
    }
    
    public static void doOut(ElevatorTable elevatorTable, RequestTable requestTable, int id) {
        ArrayList<MyPersonRequest> insideRequests = elevatorTable.getInsideRequests();
        HashMap<Integer, ArrayList<MyPersonRequest>> toFloorRequests =
            elevatorTable.getToFloorRequests();
        int currentFloor = elevatorTable.getCurrentFloor();
        String currentFloorName = TranslateFloor.getFloorName(currentFloor);
        ArrayList<MyPersonRequest> requests = toFloorRequests.get(currentFloor);
        for (MyPersonRequest request : requests) {
            TimableOutput.println("OUT-S-" + request.getPersonId() + "-" +
                currentFloorName + "-" + id);
            insideRequests.remove(request);
            requestTable.countMinus();
        }
        requests.clear();
        if (elevatorTable.isUpdated() &&
            elevatorTable.getCurrentFloor() == elevatorTable.getTransferFloor()) {
            for (MyPersonRequest request : insideRequests) {
                TimableOutput.println("OUT-F-" + request.getPersonId() + "-" +
                    TranslateFloor.getFloorName(currentFloor) + "-" + id);
                toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                    remove(request);
                request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
                requestTable.addRequest(request);
            }
            insideRequests.clear();
        }
    }
    
    public static void doIn(ElevatorTable elevatorTable, int id) {
        ArrayList<MyPersonRequest> waitingRequests = elevatorTable.getWaitingRequests();
        HashMap<Integer, ArrayList<MyPersonRequest>> fromFloorRequests =
            elevatorTable.getFromFloorRequests();
        ArrayList<MyPersonRequest> insideRequests = elevatorTable.getInsideRequests();
        HashMap<Integer, ArrayList<MyPersonRequest>> toFloorRequests =
            elevatorTable.getToFloorRequests();
        int currentFloor = elevatorTable.getCurrentFloor();
        boolean direction = elevatorTable.getDirection();
        int maxNumber = elevatorTable.getMaxNumber();
        ArrayList<MyPersonRequest> fromFloorRequests2 = fromFloorRequests.get(currentFloor);
        while (insideRequests.size() < maxNumber && !fromFloorRequests2.isEmpty()) {
            MyPersonRequest request = null;
            int priority = Integer.MIN_VALUE;
            for (MyPersonRequest myPersonRequest : fromFloorRequests2) {
                int curFloor = TranslateFloor.getFloorNumber(myPersonRequest.getCurrentFloor());
                int toFloor = TranslateFloor.getFloorNumber(myPersonRequest.getToFloor());
                boolean dir = (curFloor <= toFloor);
                if (dir == direction) {
                    if (myPersonRequest.getPriority() > priority) {
                        request = myPersonRequest;
                        priority = myPersonRequest.getPriority();
                    }
                }
            }
            if (request != null) {
                insideRequests.add(request);
                toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                        add(request);
                fromFloorRequests2.remove(request);
                waitingRequests.remove(request);
                TimableOutput.println("IN-" + request.getPersonId() +
                    "-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
            } else {
                break;
            }
        }
    }
    
    public static boolean needPreKickOut(ElevatorTable elevatorTable, int toFloor) {
        ArrayList<MyPersonRequest> insideRequests = elevatorTable.getInsideRequests();
        int currentFloor = elevatorTable.getCurrentFloor();
        int distance = Math.abs(toFloor - currentFloor);
        for (MyPersonRequest request : insideRequests) {
            if (!(elevatorTable.getDirection() == (
                TranslateFloor.getFloorNumber(request.getCurrentFloor()) <=
                TranslateFloor.getFloorNumber(request.getToFloor())) &&
                Math.abs(TranslateFloor.getFloorNumber(request.getCurrentFloor()) -
                TranslateFloor.getFloorNumber(request.getToFloor())) >= distance)) {
                return true;
            }
        }
        return false;
    }
}
