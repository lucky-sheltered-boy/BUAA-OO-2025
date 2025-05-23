import com.oocourse.elevator2.ScheRequest;
import com.oocourse.elevator2.TimableOutput;
import java.util.ArrayList;
import java.util.HashMap;

public class ElevatorThread extends Thread {
    private Integer id;
    private final ElevatorTable elevatorTable;
    private HashMap<Integer, ArrayList<MyPersonRequest>> fromFloorRequests;
    private ArrayList<MyPersonRequest> waitingRequests;
    private HashMap<Integer, ArrayList<MyPersonRequest>> toFloorRequests;
    private ArrayList<MyPersonRequest> insideRequests;
    private ArrayList<ScheRequest> scheRequests;
    private ElevatorStrategy strategy;
    private RequestTable requestTable;
    private long moveSpeed = 400;
    private long openSpeed = 400;
    private long lastTime;
    
    public ElevatorThread(Integer id, long startTime, ElevatorTable elevatorTable,
        RequestTable requestTable) {
        this.id = id;
        this.elevatorTable = elevatorTable;
        strategy = new ElevatorStrategy(elevatorTable);
        lastTime = startTime;
        fromFloorRequests = elevatorTable.getFromFloorRequests();
        waitingRequests = elevatorTable.getWaitingRequests();
        toFloorRequests = elevatorTable.getToFloorRequests();
        insideRequests = elevatorTable.getInsideRequests();
        scheRequests = elevatorTable.getScheRequests();
        this.requestTable = requestTable;
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
                    case SCHE: {
                        elevatorTable.setScheduleFlag(true);
                        break;
                    }
                    case MOVE: {
                        move(this.moveSpeed);                             //电梯沿着原方向移动一层
                        break;
                    }
                    case OPEN: {
                        openAndClose();                     //电梯开门
                        break;
                    }
                    case REVERSE: {
                        elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
                        break;
                    }
                    case WAIT: {
                        elevatorTable.setWaitFlag(true);
                        try {
                            elevatorTable.wait();//电梯等待
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        elevatorTable.setWaitFlag(false);
                        break;
                    }
                    case OVER: {
                        end = true;
                        break;
                    }
                    default: {
                    
                    }
                }
            }
            if (elevatorTable.isScheduled()) {
                schedule();
                elevatorTable.setScheduleFlag(false);
            }
        }
    }
    
    public void schedule() {
        ScheRequest scheRequest = scheRequests.remove(0);
        requestTable.countMinus();
        final long scheSpeed = (long) (scheRequest.getSpeed() * 1000);
        int toFloor = TranslateFloor.getFloorNumber(scheRequest.getToFloor());
        scheCheckFloor(toFloor);
        TimableOutput.println("SCHE-BEGIN-" + id);
        lastTime = System.currentTimeMillis();
        removeWaitingRequest();
        scheMove(scheSpeed, toFloor);
        scheKickOut();
        TimableOutput.println("SCHE-END-" + id);
        lastTime = System.currentTimeMillis();
    }
    
    private void scheKickOut() {
        int currentFloor = elevatorTable.getCurrentFloor();
        TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        final long startTime = System.currentTimeMillis();
        if (!toFloorRequests.get(currentFloor).isEmpty()) {
            String currentFloorName = TranslateFloor.getFloorName(currentFloor);
            ArrayList<MyPersonRequest> requests = toFloorRequests.get(currentFloor);
            for (MyPersonRequest request : requests) {
                TimableOutput.println("OUT-S-" + request.getPersonId() + "-" +
                    currentFloorName + "-" + id);
                insideRequests.remove(request);
                requestTable.countMinus();
            }
            requests.clear();
        }
        for (MyPersonRequest request : insideRequests) {
            TimableOutput.println("OUT-F-" + request.getPersonId() + "-" +
                TranslateFloor.getFloorName(currentFloor) + "-" + id);
            toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                remove(request);
            request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
            requestTable.addRequest(request);
        }
        insideRequests.clear();
        long endTime = System.currentTimeMillis();
        if (endTime - startTime < 1000) {
            try {
                sleep(1000 - (endTime - startTime));
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        lastTime = System.currentTimeMillis();
    }
    
    private void removeWaitingRequest() {
        for (MyPersonRequest request : waitingRequests) {
            fromFloorRequests.get(TranslateFloor.getFloorNumber(request.getCurrentFloor())).
                remove(request);
            requestTable.addRequest(request);
        }
        waitingRequests.clear();
    }
    
    public void scheCheckFloor(int toFloor) {
        int currentFloor = elevatorTable.getCurrentFloor();
        if (!toFloorRequests.get(currentFloor).isEmpty()) {
            TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
            final long startTime = System.currentTimeMillis();
            String currentFloorName = TranslateFloor.getFloorName(currentFloor);
            ArrayList<MyPersonRequest> requests = toFloorRequests.get(currentFloor);
            for (MyPersonRequest request : requests) {
                TimableOutput.println("OUT-S-" + request.getPersonId() + "-" +
                    currentFloorName + "-" + id);
                insideRequests.remove(request);
                requestTable.countMinus();
            }
            requests.clear();
            schePreKickOut(toFloor);
            long endTime = System.currentTimeMillis();
            if (endTime - startTime < openSpeed) {
                try {
                    sleep(this.openSpeed - (endTime - startTime));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
            lastTime = System.currentTimeMillis();
        } else {
            if (needPreKickOut(toFloor)) {
                TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor)
                    + "-" + id);
                long startTime = System.currentTimeMillis();
                schePreKickOut(toFloor);
                long endTime = System.currentTimeMillis();
                if (endTime - startTime < openSpeed) {
                    try {
                        sleep(this.openSpeed - (endTime - startTime));
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor)
                    + "-" + id);
                lastTime = System.currentTimeMillis();
            }
        }
    }
    
    private boolean needPreKickOut(int toFloor) {
        int currentFloor = elevatorTable.getCurrentFloor();
        int distance = Math.abs(toFloor - currentFloor);
        for (MyPersonRequest request : insideRequests) {
            if (!(elevatorTable.getDirection() == judgeDirection(
                TranslateFloor.getFloorNumber(request.getCurrentFloor()),
                TranslateFloor.getFloorNumber(request.getToFloor())) &&
                Math.abs(TranslateFloor.getFloorNumber(request.getCurrentFloor()) -
                TranslateFloor.getFloorNumber(request.getToFloor())) >= distance)) {
                return true;
            }
        }
        return false;
    }
    
    public void schePreKickOut(int toFloor) {
        int currentFloor = elevatorTable.getCurrentFloor();
        int distance = Math.abs(toFloor - currentFloor);
        ArrayList<MyPersonRequest> removeList = new ArrayList<>();
        for (MyPersonRequest request : insideRequests) {
            if (!(elevatorTable.getDirection() == judgeDirection(
                TranslateFloor.getFloorNumber(request.getCurrentFloor()),
                TranslateFloor.getFloorNumber(request.getToFloor())) &&
                Math.abs(TranslateFloor.getFloorNumber(request.getCurrentFloor()) -
                TranslateFloor.getFloorNumber(request.getToFloor())) >= distance)) {
                removeList.add(request);
                toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                    remove(request);
                request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
                TimableOutput.println("OUT-F-" + request.getPersonId() +
                    "-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
                requestTable.addRequest(request);
            }
        }
        for (MyPersonRequest request : removeList) {
            insideRequests.remove(request);
        }
    }
    
    public void scheMove(long scheSpeed, int toFloor) {
        int eleCurFloor = elevatorTable.getCurrentFloor();
        if (eleCurFloor != toFloor &&
            elevatorTable.getDirection() != (toFloor > eleCurFloor)) {
            elevatorTable.setDirection(!elevatorTable.getDirection());
        }
        int moveTime = Math.abs(toFloor - eleCurFloor);
        for (int i = 0; i < moveTime; i++) {
            long nowTime = System.currentTimeMillis();
            if (elevatorTable.getCurrentNum() > 0) {
                if (nowTime - lastTime < scheSpeed) {
                    try {
                        sleep(scheSpeed - (nowTime - lastTime));
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            } else {
                try {
                    sleep(scheSpeed);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            moveOneFloor();
            TimableOutput.println("ARRIVE-" +
                TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            this.lastTime = System.currentTimeMillis();
        }
    }
    
    public void move(long moveSpeed) {
        long nowTime = System.currentTimeMillis();
        if (elevatorTable.getCurrentNum() > 0) {
            if (nowTime - lastTime < moveSpeed) {
                try {
                    elevatorTable.wait(moveSpeed - (nowTime - lastTime));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        } else {
            try {
                elevatorTable.wait(moveSpeed);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        Advice advice = strategy.getAdvice();
        if (advice == Advice.MOVE) {
            moveOneFloor();
            TimableOutput.println("ARRIVE-" +
                TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            this.lastTime = System.currentTimeMillis();
        } else if (advice == Advice.SCHE) {
            int toFloor = TranslateFloor.getFloorNumber(scheRequests.get(0).getToFloor());
            int curFloor = elevatorTable.getCurrentFloor();
            if (toFloor != curFloor) {
                if (elevatorTable.getDirection() == (toFloor > curFloor)) {
                    moveOneFloor();
                    TimableOutput.println("ARRIVE-" +
                        TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
                    this.lastTime = System.currentTimeMillis();
                }
            }
        }
    }
    
    public void moveOneFloor() {
        boolean direction = elevatorTable.getDirection();
        int afterFloor = direction ? elevatorTable.getCurrentFloor() + 1 :
            elevatorTable.getCurrentFloor() - 1;
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
        ArrayList<MyPersonRequest> requests = toFloorRequests.get(currentFloor);
        for (MyPersonRequest request : requests) {
            TimableOutput.println("OUT-S-" + request.getPersonId() + "-" +
                currentFloorName + "-" + id);
            insideRequests.remove(request);
            requestTable.countMinus();
        }
        requests.clear();
    }
    
    public void doIn() {
        int currentFloor = elevatorTable.getCurrentFloor();
        boolean direction = elevatorTable.getDirection();
        int maxNumber = elevatorTable.getMaxNumber();
        ArrayList<MyPersonRequest> fromFloorRequests2 = fromFloorRequests.get(currentFloor);
        while (getCurrentNum() < maxNumber && !fromFloorRequests2.isEmpty()) {
            MyPersonRequest request = null;
            int priority = Integer.MIN_VALUE;
            for (MyPersonRequest myPersonRequest : fromFloorRequests2) {
                int curFloor = TranslateFloor.getFloorNumber(myPersonRequest.getCurrentFloor());
                int toFloor = TranslateFloor.getFloorNumber(myPersonRequest.getToFloor());
                boolean dir = judgeDirection(curFloor, toFloor);
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
    
    public boolean judgeDirection(int fromFloor, int toFloor) {
        return fromFloor <= toFloor;
    }
}
