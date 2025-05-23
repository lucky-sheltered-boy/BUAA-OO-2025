import com.oocourse.elevator3.Request;
import com.oocourse.elevator3.ScheRequest;
import com.oocourse.elevator3.TimableOutput;

import java.util.ArrayList;
import java.util.HashMap;

public class ElevatorTable {
    private HashMap<Integer, ArrayList<MyPersonRequest>> fromFloorRequests;
    private ArrayList<MyPersonRequest> waitingRequests;
    private HashMap<Integer, ArrayList<MyPersonRequest>> toFloorRequests;
    private ArrayList<MyPersonRequest> insideRequests;
    private ArrayList<ScheRequest> scheRequests;
    private ArrayList<MyUpdateRequest> myUpdateRequests;
    private Integer maxNumber;
    private Integer currentFloor = 1;
    private boolean direction; // true for up, false for down
    private int elevatorId;
    private long lastTime;
    private int transferFloor;
    private int topFloor = 7;
    private int bottomFloor = -3;
    private boolean endFlag = false;
    private boolean waitFlag = false;
    private boolean isScheduled = false;
    private boolean isBeingUpdated = false;
    private boolean isUpdated = false;
    private boolean isA = false;
    
    public ElevatorTable(int elevatorId, int maxNumber, boolean direction, long lastTime) {
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
        this.myUpdateRequests = new ArrayList<>();
        this.elevatorId = elevatorId;
        this.maxNumber = maxNumber;
        this.direction = direction;
        this.lastTime = lastTime;
    }
    
    public synchronized void addRequest(Request request) {
        if (waitFlag) {
            this.notifyAll();
        }
        if (request instanceof MyPersonRequest) {
            TimableOutput.println("RECEIVE-" + ((MyPersonRequest) request).getPersonId()
                + "-" + elevatorId);
            if (waitingRequests.isEmpty() && insideRequests.isEmpty()) {
                setLastTime(System.currentTimeMillis());
            }
            waitingRequests.add((MyPersonRequest) request);
            fromFloorRequests.get(TranslateFloor.getFloorNumber(((MyPersonRequest) request).
                getCurrentFloor())).add((MyPersonRequest) request);
        } else if (request instanceof ScheRequest) {
            scheRequests.add((ScheRequest) request);
            if (Debug.debug()) {
                TimableOutput.println("[LOG] elevator-" + elevatorId + "-receive-SCHE");
            }
        } else if (request instanceof MyUpdateRequest) {
            myUpdateRequests.add((MyUpdateRequest) request);
            if (Debug.debug()) {
                TimableOutput.println("[LOG] elevator-" + elevatorId + "-receive-UPDATE");
            }
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
    
    public ArrayList<MyUpdateRequest> getMyUpdateRequests() {
        return myUpdateRequests;
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
    
    public void setBeingUpdateFlag(boolean isBeingUpdated) {
        this.isBeingUpdated = isBeingUpdated;
    }
    
    public boolean isBeingUpdated() {
        return isBeingUpdated;
    }
    
    public void setUpdatedFlag(boolean isUpdated) {
        this.isUpdated = isUpdated;
    }
    
    public boolean isUpdated() {
        return isUpdated;
    }
    
    public void setAFlag(boolean isA) {
        this.isA = isA;
    }
    
    public boolean isA() {
        return isA;
    }
    
    public void setTransferFloor(int transferFloor) {
        this.transferFloor = transferFloor;
    }
    
    public int getTransferFloor() {
        return transferFloor;
    }
    
    public int getElevatorId() {
        return elevatorId;
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
    
    public void setLastTime(long lastTime) {
        this.lastTime = lastTime;
    }
    
    public long getLastTime() {
        return lastTime;
    }
    
    public int getTopFloor() {
        return topFloor;
    }
    
    public int getBottomFloor() {
        return bottomFloor;
    }
    
    public void setTopFloor(int topFloor) {
        this.topFloor = topFloor;
    }
    
    public void setBottomFloor(int bottomFloor) {
        this.bottomFloor = bottomFloor;
    }
    
    public int isCurFloorNotQualified(MyPersonRequest request) {
        int topFloor = this.topFloor;
        int bottomFloor = this.bottomFloor;
        int curFloor = TranslateFloor.getFloorNumber(request.getCurrentFloor());
        return curFloor >= bottomFloor && curFloor <= topFloor ? 0 : 1;
    }
    
    public int isToFloorNotQualified(MyPersonRequest request) {
        int topFloor = this.topFloor;
        int bottomFloor = this.bottomFloor;
        int toFloor = TranslateFloor.getFloorNumber(request.getToFloor());
        return toFloor >= bottomFloor && toFloor <= topFloor ? 0 : 1;
    }
    
    public int isNeedless(MyPersonRequest request) {
        int topFloor = this.topFloor;
        int bottomFloor = this.bottomFloor;
        int curFloor = TranslateFloor.getFloorNumber(request.getCurrentFloor());
        int toFloor = TranslateFloor.getFloorNumber(request.getToFloor());
        return (curFloor >= topFloor && toFloor >= topFloor ||
               curFloor <= bottomFloor && toFloor <= bottomFloor) ? 1 : 0;
    }
}
