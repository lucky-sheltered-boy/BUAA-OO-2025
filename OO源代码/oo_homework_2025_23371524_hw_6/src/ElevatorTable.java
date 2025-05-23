import com.oocourse.elevator2.Request;
import com.oocourse.elevator2.ScheRequest;
import com.oocourse.elevator2.TimableOutput;

import java.util.ArrayList;
import java.util.HashMap;

public class ElevatorTable {
    private HashMap<Integer, ArrayList<MyPersonRequest>> fromFloorRequests;
    private ArrayList<MyPersonRequest> waitingRequests;
    private HashMap<Integer, ArrayList<MyPersonRequest>> toFloorRequests;
    private ArrayList<MyPersonRequest> insideRequests;
    private ArrayList<ScheRequest> scheRequests;
    private Integer maxNumber;
    private Integer currentFloor = 1;
    private boolean direction; // true for up, false for down
    private int elevatorId;
    private boolean endFlag = false;
    private boolean waitFlag = false;
    private boolean isScheduled = false;
    
    public ElevatorTable(int elevatorId, int maxNumber, boolean direction) {
        this.fromFloorRequests = new HashMap<>();
        for (int i = -4; i <= 7; i++) {
            fromFloorRequests.put(i, new ArrayList<>());
        }
        this.waitingRequests = new ArrayList<>();
        this.toFloorRequests = new HashMap<>();
        for (int i = -4; i <= 7; i++) {
            toFloorRequests.put(i, new ArrayList<>());
        }
        this.insideRequests = new ArrayList<>();
        this.scheRequests = new ArrayList<>();
        this.elevatorId = elevatorId;
        this.maxNumber = maxNumber;
        this.direction = direction;
    }
    
    public synchronized void addRequest(Request request) {
        if (waitFlag) {
            this.notifyAll();
        }
        if (request instanceof MyPersonRequest) {
            TimableOutput.println("RECEIVE-" + ((MyPersonRequest) request).getPersonId()
                + "-" + elevatorId);
            waitingRequests.add((MyPersonRequest) request);
            fromFloorRequests.get(TranslateFloor.getFloorNumber(((MyPersonRequest) request).
                getCurrentFloor())).add((MyPersonRequest) request);
        } else {
            scheRequests.add((ScheRequest) request);
        }
    }
    
    public synchronized void setEndFlag() {
        if (waitFlag) {
            this.notifyAll();
        }
        endFlag = true;
    }
    
    public synchronized boolean isEnd() {
        return endFlag;
    }
    
    public HashMap<Integer, ArrayList<MyPersonRequest>> getFromFloorRequests() {
        return fromFloorRequests;
    }
    
    public ArrayList<MyPersonRequest> getWaitingRequests() {
        return waitingRequests;
    }
    
    public HashMap<Integer, ArrayList<MyPersonRequest>> getToFloorRequests() {
        return toFloorRequests;
    }
    
    public ArrayList<MyPersonRequest> getInsideRequests() {
        return insideRequests;
    }
    
    public ArrayList<ScheRequest> getScheRequests() {
        return scheRequests;
    }
    
    public Integer getCurrentFloor() {
        return currentFloor;
    }
    
    public void setCurrentFloor(Integer currentFloor) {
        this.currentFloor = currentFloor;
    }
    
    public boolean getDirection() {
        return direction;
    }
    
    public void setDirection(boolean direction) {
        this.direction = direction;
    }
    
    public Integer getMaxNumber() {
        return maxNumber;
    }
    
    public Integer getCurrentNum() {
        return insideRequests.size();
    }
    
    public Integer getTotalNum() {
        return waitingRequests.size() + insideRequests.size();
    }
    
    public boolean isFull() {
        return insideRequests.size() >= maxNumber;
    }
    
    public void setWaitFlag(boolean waitFlag) {
        this.waitFlag = waitFlag;
    }
    
    public void setScheduleFlag(boolean isScheduled) {
        this.isScheduled = isScheduled;
    }
    
    public boolean isScheduled() {
        return isScheduled;
    }
    
    public int getFarthestFloorInEle() {
        int farthestFloor = currentFloor;
        for (MyPersonRequest request : insideRequests) {
            if (direction) {
                if (TranslateFloor.getFloorNumber(request.getToFloor()) > farthestFloor) {
                    farthestFloor = TranslateFloor.getFloorNumber(request.getToFloor());
                }
            } else {
                if (TranslateFloor.getFloorNumber(request.getToFloor()) < farthestFloor) {
                    farthestFloor = TranslateFloor.getFloorNumber(request.getToFloor());
                }
            }
        }
        return farthestFloor;
    }
    
    public synchronized int getFarthestFloorInQue(int curFloor, boolean direction) {
        int farthestFloor = getFarthestFloorInEle();
        int flag = 0;
        for (MyPersonRequest request : waitingRequests) {
            if (direction) {
                if (TranslateFloor.getFloorNumber(request.getCurrentFloor()) >= curFloor &&
                    TranslateFloor.getFloorNumber(request.getToFloor()) > farthestFloor) {
                    farthestFloor = TranslateFloor.getFloorNumber(request.getToFloor());
                    flag = 1;
                }
            } else {
                if (TranslateFloor.getFloorNumber(request.getCurrentFloor()) <= curFloor &&
                    TranslateFloor.getFloorNumber(request.getToFloor()) < farthestFloor) {
                    farthestFloor = TranslateFloor.getFloorNumber(request.getToFloor());
                    flag = 1;
                }
            }
        }
        if (flag == 1) {
            if (direction) {
                farthestFloor += 2; // 加一个偏移量
            } else {
                farthestFloor -= 2; // 加一个偏移量
            }
        }
        return farthestFloor;
    }
    
    public int getAllPriority() {
        int priority = 0;
        for (MyPersonRequest request : waitingRequests) {
            priority += request.getPriority();
        }
        for (MyPersonRequest request : insideRequests) {
            priority += request.getPriority();
        }
        return priority;
    }
}
