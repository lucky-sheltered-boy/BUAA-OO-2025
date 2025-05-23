import com.oocourse.elevator3.Request;
import com.oocourse.elevator3.ScheRequest;

import java.util.HashMap;

public class DispatchStrategy {
    private RequestTable requestTable;
    private HashMap<Integer, ElevatorTable> elevatorTableMap;
    
    public DispatchStrategy(RequestTable requestTable, HashMap<Integer,
        ElevatorTable> elevatorTableMap) {
        this.requestTable = requestTable;
        this.elevatorTableMap = elevatorTableMap;
    }
    
    public boolean dispatch() {
        Request request = requestTable.getRequest();
        if (request == null) {
            return false;
        }
        Integer bestElevator = getBestEle(request);
        //没有合适的就返回null,继续递归寻找下一个，return后再把现在那个给加回去
        if (bestElevator == -1) {
            requestTable.setReturnNullFlag(true);
            boolean isDisped = dispatch();
            requestTable.addRequest(request);
            requestTable.setReturnNullFlag(false);
            return isDisped;
        }
        return true;
    }
    
    private Integer getBestEle(Request request) {
        int bestElevator = -1;
        if (request instanceof ScheRequest) {
            bestElevator = ((ScheRequest) request).getElevatorId();
            elevatorTableMap.get(bestElevator).addRequest(request);
        } else if (request instanceof MyUpdateRequest) {
            final int transferFloor = TranslateFloor.getFloorNumber(((MyUpdateRequest) request).
                getTransferFloor());
            bestElevator = ((MyUpdateRequest) request).getElevatorAId();
            elevatorTableMap.get(bestElevator).addRequest(request);
            elevatorTableMap.get(bestElevator).setAFlag(true);
            elevatorTableMap.get(bestElevator).setTransferFloor(transferFloor);
            bestElevator = ((MyUpdateRequest) request).getElevatorBId();
            elevatorTableMap.get(bestElevator).addRequest(request);
            elevatorTableMap.get(bestElevator).setTransferFloor(transferFloor);
        } else {
            MyPersonRequest myPersonRequest = (MyPersonRequest) request;
            synchronized (elevatorTableMap.get(1)) {
                synchronized (elevatorTableMap.get(2)) {
                    synchronized (elevatorTableMap.get(3)) {
                        synchronized (elevatorTableMap.get(4)) {
                            synchronized (elevatorTableMap.get(5)) {
                                synchronized (elevatorTableMap.get(6)) {
                                    double scoreMax = -1000000000;
                                    int maxNum = 13;
                                    for (int i = 1; i <= 6; i++) {
                                        ElevatorTable elevatorTable = elevatorTableMap.get(i);
                                        if (!elevatorTable.isScheduled() &&
                                            !elevatorTable.isBeingUpdated() &&
                                            elevatorTable.
                                            isCurFloorNotQualified(myPersonRequest) == 0 &&
                                            elevatorTable.isNeedless(myPersonRequest) == 0 &&
                                            elevatorTable.getTotalNum() < maxNum) {
                                            double scoreTemp = calculateScore(elevatorTable,
                                                myPersonRequest);
                                            if (scoreTemp > scoreMax) {
                                                bestElevator = i;
                                                scoreMax = scoreTemp;
                                            }
                                        }
                                    }
                                    if (bestElevator != -1) {
                                        elevatorTableMap.get(bestElevator).addRequest(request);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        return bestElevator;
    }
    
    public double calculateScore(ElevatorTable elevatorTable, MyPersonRequest person) {
        int reCurFloor = TranslateFloor.getFloorNumber(person.getCurrentFloor());
        int reToFloor = TranslateFloor.getFloorNumber(person.getToFloor());
        int eleCurFloor = elevatorTable.getCurrentFloor();
        boolean direction = elevatorTable.getDirection();
        int curPeoNum = elevatorTable.getCurrentNum();
        int totalPeoNum = elevatorTable.getTotalNum();
        int allPriority = elevatorTable.getAllPriority();
        int speed = elevatorTable.isUpdated() ? 200 : 400;
        int distance = getDistance(reCurFloor, reToFloor, eleCurFloor,
            direction, person, elevatorTable);
        double result = 21 - 2.0 * distance - 2.5 * curPeoNum - 2.5 * totalPeoNum
            - 10.0 * (double)speed / 100 - 3.5 * (double)allPriority / 100
            - 30.0 * elevatorTable.isToFloorNotQualified(person);
        return result;
    }
    
    public synchronized int getDistance(int reCurFloor, int reToFloor, int eleCurFloor,
        boolean direction, MyPersonRequest person, ElevatorTable elevatorTable) {
        if (reCurFloor == eleCurFloor) {
            return 0;
        }
        int farthestFloorInEle = elevatorTable.getFarthestFloorInEle();
        int farthestFloorInQue = elevatorTable.getFarthestFloorInQue(eleCurFloor, direction);
        int tempFloor;
        if ((farthestFloorInEle > farthestFloorInQue) == direction) {
            tempFloor = farthestFloorInEle;
        } else {
            tempFloor = farthestFloorInQue;
        }
        if ((reCurFloor > eleCurFloor) == direction) {
            if ((reToFloor > reCurFloor) == direction) {
                return Math.abs(reCurFloor - eleCurFloor);
            } else {
                return Math.abs(tempFloor - eleCurFloor) + Math.abs(tempFloor - reCurFloor);
            }
        }
        if (direction) {
            if (person.getDirection()) {
                return Math.abs(tempFloor - eleCurFloor) + (tempFloor + 3) + (reCurFloor + 3);
            } else {
                return Math.abs(tempFloor - eleCurFloor) + Math.abs(tempFloor - reCurFloor);
            }
        } else {
            if (person.getDirection()) {
                return Math.abs(tempFloor - eleCurFloor) + Math.abs(tempFloor - reCurFloor);
            } else {
                return Math.abs(tempFloor - eleCurFloor) + Math.abs(tempFloor - 7) +
                    Math.abs(reCurFloor - 7);
            }
        }
    }
}
