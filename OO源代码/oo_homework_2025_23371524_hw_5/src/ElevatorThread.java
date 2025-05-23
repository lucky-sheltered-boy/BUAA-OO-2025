import com.oocourse.elevator1.PersonRequest;
import com.oocourse.elevator1.TimableOutput;
import java.util.ArrayList;
import java.util.HashMap;

public class ElevatorThread extends Thread {
    private Integer id;
    private final ElevatorTable elevatorTable;
    private HashMap<Integer, ArrayList<PersonRequest>> fromFloorRequests;
    private ArrayList<PersonRequest> waitingRequests;
    private HashMap<Integer, ArrayList<PersonRequest>> toFloorRequests;
    private ArrayList<PersonRequest> insideRequests;
    private ElevatorStrategy strategy;
    private long moveSpeed = 400;
    private long openSpeed = 400;
    private long lastTime;
    
    public ElevatorThread(Integer id, long startTime, ElevatorTable elevatorTable) {
        this.id = id;
        this.elevatorTable = elevatorTable;
        strategy = new ElevatorStrategy(elevatorTable);
        lastTime = startTime;
        fromFloorRequests = elevatorTable.getFromFloorRequests();
        waitingRequests = elevatorTable.getWaitingRequests();
        toFloorRequests = elevatorTable.getToFloorRequests();
        insideRequests = elevatorTable.getInsideRequests();
    }
    
    public Integer getCurrentFloor() {
        return elevatorTable.getCurrentFloor();
    }
    
    public Integer getCurrentNum() {
        return insideRequests.size();
    }
    
    public boolean isFull() {
        return elevatorTable.isFull();
    }

    @Override
    public void run() {
        boolean end = false;
        while (!end) {
            synchronized (elevatorTable) {
                Advice advice = strategy.getAdvice();
                switch (advice) {
                    case MOVE:
                        move();                             //电梯沿着原方向移动一层
                        break;
                    case OPEN:
                        openAndClose();                     //电梯开门
                        break;
                    case REVERSE:
                        elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
                        break;
                    case WAIT:
                        try {
                            elevatorTable.setWaitFlag(true);
                            elevatorTable.wait();//电梯等待
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        elevatorTable.setWaitFlag(false);
                        break;
                    case OVER:
                        end = true;
                        break;
                    default:
                }
            }
        }
    }
    
    public void move() {
        long nowTime = System.currentTimeMillis();
        if (nowTime - lastTime < moveSpeed) {
            try {
                elevatorTable.wait(moveSpeed - (nowTime - lastTime));
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        if (strategy.getAdvice() == Advice.MOVE) {
            moveOneFloor();
            TimableOutput.println("ARRIVE-" +
                TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            this.lastTime = System.currentTimeMillis();
        }
    }
    
    public void moveOneFloor() {
        boolean direction = elevatorTable.getDirection();
        int afterFloor;
        if (direction) {
            afterFloor = elevatorTable.getCurrentFloor() + 1;
            if (afterFloor == 0) {
                afterFloor = 1;
            }
        } else {
            afterFloor = elevatorTable.getCurrentFloor() - 1;
            if (afterFloor == 0) {
                afterFloor = -1;
            }
        }
        elevatorTable.setCurrentFloor(afterFloor);
    }
    
    public void openAndClose() {
        int currentFloor = elevatorTable.getCurrentFloor();
        TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        doOut();
        try {
            elevatorTable.wait(this.openSpeed);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (strategy.getAdvice() == Advice.REVERSE) {
            elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
        }
        doIn();
        TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        lastTime = System.currentTimeMillis();
    }
    
    public void doOut() {
        int currentFloor = elevatorTable.getCurrentFloor();
        String currentFloorName = TranslateFloor.getFloorName(currentFloor);
        ArrayList<PersonRequest> requests = toFloorRequests.get(currentFloor);
        for (PersonRequest request : requests) {
            TimableOutput.println("OUT-" + request.getPersonId() + "-" +
                currentFloorName + "-" + id);
            insideRequests.remove(request);
        }
        requests.clear();
        for (PersonRequest request : insideRequests) {
            TimableOutput.println("OUT-" + request.getPersonId() + "-" +
                currentFloorName + "-" + id);
            ArrayList<PersonRequest> requests2 = toFloorRequests.get(TranslateFloor.
                getFloorNumber(request.getToFloor()));
            requests2.remove(request);
            waitingRequests.add(request);
            ArrayList<PersonRequest> requests3 = fromFloorRequests.get(currentFloor);
            requests3.add(request);
        }
        insideRequests.clear();
    }
    
    public void doIn() {
        int currentFloor = elevatorTable.getCurrentFloor();
        boolean direction = elevatorTable.getDirection();
        int maxNumber = elevatorTable.getMaxNumber();
        ArrayList<PersonRequest> fromFloorRequests2 = fromFloorRequests.get(currentFloor);
        while (getCurrentNum() < maxNumber && !fromFloorRequests2.isEmpty()) {
            PersonRequest request = null;
            int priority = Integer.MIN_VALUE;
            for (PersonRequest personRequest : fromFloorRequests2) {
                int fromFloor = TranslateFloor.getFloorNumber(personRequest.getFromFloor());
                int toFloor = TranslateFloor.getFloorNumber(personRequest.getToFloor());
                boolean dir = judgeDirection(fromFloor, toFloor);
                if (dir == direction) {
                    if (personRequest.getPriority() > priority) {
                        request = personRequest;
                        priority = personRequest.getPriority();
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
    
    public boolean judgeDirection(int fromFloor, int toFloor) {
        return fromFloor <= toFloor;
    }
}
