import com.oocourse.elevator1.PersonRequest;
//import com.oocourse.elevator1.TimableOutput;
import java.util.ArrayList;
import java.util.HashMap;

public class ElevatorTable {
    private HashMap<Integer, ArrayList<PersonRequest>> fromFloorRequests;
    private ArrayList<PersonRequest> waitingRequests;
    private HashMap<Integer, ArrayList<PersonRequest>> toFloorRequests;
    private ArrayList<PersonRequest> insideRequests;
    private Integer maxNumber;
    private Integer currentFloor = 1;
    private boolean direction; // true for up, false for down
    private int elevatorId;
    private boolean endFlag = false;
    private boolean waitFlag = false;
    
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
        this.elevatorId = elevatorId;
        this.maxNumber = maxNumber;
        this.direction = direction;
    }
    
    public synchronized void addRequest(PersonRequest request) {
        if (waitFlag) {
            this.notifyAll();
        }
        waitingRequests.add(request);
        fromFloorRequests.get(getFromFloor(request)).add(request);
    }
    
    public synchronized void setEndFlag() {
        if (waitFlag) {
            this.notifyAll();
        }
        endFlag = true;
    }
    
    public synchronized boolean isEnd() {
        if (waitFlag) {
            this.notifyAll();
        }
        return endFlag;
    }
    
    public synchronized boolean isEmpty() {
        if (waitFlag) {
            this.notifyAll();
        }
        return waitingRequests.isEmpty();
    }
    
    public Integer getFromFloor(PersonRequest request) {
        String fromFloor = request.getFromFloor();
        return TranslateFloor.getFloorNumber(fromFloor);
    }
    
    public HashMap<Integer, ArrayList<PersonRequest>> getFromFloorRequests() {
        return fromFloorRequests;
    }
    
    public ArrayList<PersonRequest> getWaitingRequests() {
        return waitingRequests;
    }
    
    public HashMap<Integer, ArrayList<PersonRequest>> getToFloorRequests() {
        return toFloorRequests;
    }
    
    public ArrayList<PersonRequest> getInsideRequests() {
        return insideRequests;
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
    
    public boolean isFull() {
        return insideRequests.size() >= maxNumber;
    }
    
    public void setWaitFlag(boolean waitFlag) {
        this.waitFlag = waitFlag;
    }
    
    public int getElevatorId() {
        return elevatorId;
    }
}
