import com.oocourse.elevator3.ScheRequest;
import com.oocourse.elevator3.TimableOutput;
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
    private ArrayList<MyUpdateRequest> myUpdateRequests;
    private UpdateLock updateLock;
    private TransferFloorLock transferFloorLock;
    private ElevatorStrategy strategy;
    private RequestTable requestTable;
    private long moveSpeed = 400;
    private long openSpeed = 400;
    private boolean isUpdateMove = false;
    
    public ElevatorThread(Integer id, ElevatorTable elevatorTable, RequestTable requestTable) {
        this.id = id;
        this.elevatorTable = elevatorTable;
        strategy = new ElevatorStrategy(elevatorTable);
        fromFloorRequests = elevatorTable.getFromFloorRequests();
        waitingRequests = elevatorTable.getWaitingRequests();
        toFloorRequests = elevatorTable.getToFloorRequests();
        insideRequests = elevatorTable.getInsideRequests();
        scheRequests = elevatorTable.getScheRequests();
        myUpdateRequests = elevatorTable.getMyUpdateRequests();
        this.requestTable = requestTable;
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
                    case UPDATE: {
                        elevatorTable.setBeingUpdateFlag(true);
                        break;
                    }
                    case MOVE: {
                        if (elevatorTable.isUpdated()) {
                            isUpdateMove = true;
                            break;
                        } else {
                            normalMove(moveSpeed, false);
                        }
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
                        if (elevatorTable.isUpdated() &&
                            elevatorTable.getCurrentFloor() == elevatorTable.getTransferFloor()) {
                            moveAwayFromTransferFloor();
                            break;
                        }
                        elevatorTable.setWaitFlag(true);
                        try { elevatorTable.wait(); }
                        catch (InterruptedException e) { e.printStackTrace(); }
                        elevatorTable.setWaitFlag(false);
                        break;
                    }
                    case OVER: {
                        end = true;
                        break;
                    }
                    default: { }
                }
            }
            examine();
        }
    }
    
    public void examine() {
        if (elevatorTable.isScheduled()) {
            schedule();
            elevatorTable.setScheduleFlag(false);
        }
        if (elevatorTable.isBeingUpdated()) {
            update();
            elevatorTable.setBeingUpdateFlag(false);
            if (Debug.debug()) {
                TimableOutput.println("[LOG] elevator-" + id + "-end-UPDATE");
            }
        }
        if (isUpdateMove) {
            updateMove(moveSpeed);
            isUpdateMove = false;
        }
    }
    
    public void moveAwayFromTransferFloor() {
        elevatorTable.setDirection(elevatorTable.isA());
        long nowTime = System.currentTimeMillis();
        if (nowTime - elevatorTable.getLastTime() < moveSpeed) {
            try { elevatorTable.wait(moveSpeed - (nowTime - elevatorTable.getLastTime())); }
            catch (InterruptedException e) { e.printStackTrace(); }
        }
        moveOneFloor();
        TimableOutput.println("ARRIVE-" +
            TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
        transferFloorLock.releaseTransferFloor();
        elevatorTable.setLastTime(System.currentTimeMillis());
    }
    
    public void update() {
        MyUpdateRequest myUpdateRequest = myUpdateRequests.remove(0);
        requestTable.countMinus();
        this.updateLock = myUpdateRequest.getUpdateLock();
        this.transferFloorLock = myUpdateRequest.getTransferFloorLock();
        updateCheckFloor();
        if (Debug.debug()) {
            TimableOutput.println("[LOG] elevator-" + id + "-finish-updateCheckFloor");
        }
        updateLock.plusNumOfReadyEle();
        if (Debug.debug()) {
            TimableOutput.println("[LOG] elevator-" + id + "-finish-plusNumOfReadyEle");
        }
        synchronized (transferFloorLock) {
            try { transferFloorLock.wait(); }
            catch (InterruptedException e) { e.printStackTrace(); }
        }
        if (Debug.debug()) {
            TimableOutput.println("[LOG] elevator-" + id + "-wakefromtransferFloorLock");
        }
        removeWaitingRequest();
        if (elevatorTable.isA()) {
            elevatorTable.setCurrentFloor(elevatorTable.getTransferFloor() + 1);
            elevatorTable.setBottomFloor(elevatorTable.getTransferFloor());
        } else {
            elevatorTable.setCurrentFloor(elevatorTable.getTransferFloor() - 1);
            elevatorTable.setTopFloor(elevatorTable.getTransferFloor());
        }
        this.moveSpeed = 200;
        elevatorTable.setUpdatedFlag(true);
    }
    
    public void updateCheckFloor() {
        if (strategy.getAdvice() == Advice.REVERSE) {
            elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
        }
        if (strategy.getAdvice() == Advice.OPEN) {
            int currentFloor = elevatorTable.getCurrentFloor();
            TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
            CheckStyle.doOut(elevatorTable, requestTable, id);
            try { sleep(this.openSpeed); }
            catch (InterruptedException e) { e.printStackTrace(); }
            if (strategy.getAdvice() == Advice.REVERSE) {
                elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
            }
            CheckStyle.doIn(elevatorTable, id);
            if (!toFloorRequests.get(CheckStyle.nextFloor(elevatorTable)).isEmpty()) {
                TimableOutput.println("CLOSE-" + TranslateFloor.
                    getFloorName(currentFloor) + "-" + id);
                elevatorTable.setLastTime(System.currentTimeMillis());
                long nowTime = System.currentTimeMillis();
                if (nowTime - elevatorTable.getLastTime() < moveSpeed) {
                    try { sleep(moveSpeed - (nowTime - elevatorTable.getLastTime())); }
                    catch (InterruptedException e) { e.printStackTrace(); }
                }
                moveOneFloor();
                TimableOutput.println("ARRIVE-" + TranslateFloor.
                    getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
                elevatorTable.setLastTime(System.currentTimeMillis());
                currentFloor = elevatorTable.getCurrentFloor();
                TimableOutput.println("OPEN-" + TranslateFloor.
                    getFloorName(currentFloor) + "-" + id);
                CheckStyle.doOut(elevatorTable, requestTable, id);
                for (MyPersonRequest request : insideRequests) {
                    TimableOutput.println("OUT-F-" + request.getPersonId() + "-" +
                        TranslateFloor.getFloorName(currentFloor) + "-" + id);
                    toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                            remove(request);
                    request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
                    requestTable.addRequest(request);
                }
                insideRequests.clear();
                try { sleep(this.openSpeed); }
                catch (InterruptedException e) { e.printStackTrace(); }
            } else {
                CheckStyle.doOut(elevatorTable, requestTable, id);
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
            TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
            elevatorTable.setLastTime(System.currentTimeMillis());
        } else {
            updateCheckFloor2();
        }
    }
    
    public void updateCheckFloor2() {
        if (!toFloorRequests.get(CheckStyle.nextFloor(elevatorTable)).isEmpty()) {
            long nowTime = System.currentTimeMillis();
            if (nowTime - elevatorTable.getLastTime() < moveSpeed) {
                try { sleep(moveSpeed - (nowTime - elevatorTable.getLastTime())); }
                catch (InterruptedException e) { e.printStackTrace(); }
            }
            moveOneFloor();
            TimableOutput.println("ARRIVE-" + TranslateFloor.
                getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            elevatorTable.setLastTime(System.currentTimeMillis());
            int currentFloor = elevatorTable.getCurrentFloor();
            TimableOutput.println("OPEN-" + TranslateFloor.
                getFloorName(currentFloor) + "-" + id);
            CheckStyle.doOut(elevatorTable, requestTable, id);
            for (MyPersonRequest request : insideRequests) {
                TimableOutput.println("OUT-F-" + request.getPersonId() + "-" +
                    TranslateFloor.getFloorName(currentFloor) + "-" + id);
                toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                    remove(request);
                request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
                requestTable.addRequest(request);
            }
            insideRequests.clear();
            try { sleep(this.openSpeed); }
            catch (InterruptedException e) { e.printStackTrace(); }
            TimableOutput.println("CLOSE-" + TranslateFloor.
                getFloorName(currentFloor) + "-" + id);
            elevatorTable.setLastTime(System.currentTimeMillis());
        } else {
            if (!insideRequests.isEmpty()) {
                int currentFloor = elevatorTable.getCurrentFloor();
                TimableOutput.println("OPEN-" + TranslateFloor.
                    getFloorName(currentFloor) + "-" + id);
                CheckStyle.doOut(elevatorTable, requestTable, id);
                for (MyPersonRequest request : insideRequests) {
                    TimableOutput.println("OUT-F-" + request.getPersonId() + "-" +
                        TranslateFloor.getFloorName(currentFloor) + "-" + id);
                    toFloorRequests.get(TranslateFloor.getFloorNumber(request.getToFloor())).
                        remove(request);
                    request.setCurrentFloor(TranslateFloor.getFloorName(currentFloor));
                    requestTable.addRequest(request);
                }
                insideRequests.clear();
                try { sleep(this.openSpeed); }
                catch (InterruptedException e) { e.printStackTrace(); }
                TimableOutput.println("CLOSE-" + TranslateFloor.
                    getFloorName(currentFloor) + "-" + id);
                elevatorTable.setLastTime(System.currentTimeMillis());
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
        elevatorTable.setLastTime(System.currentTimeMillis());
        removeWaitingRequest();
        scheMove(scheSpeed, toFloor);
        scheKickOut();
        TimableOutput.println("SCHE-END-" + id);
        elevatorTable.setLastTime(System.currentTimeMillis());
    }
    
    private void scheKickOut() {
        int currentFloor = elevatorTable.getCurrentFloor();
        TimableOutput.println("OPEN-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        final long startTime = System.currentTimeMillis();
        CheckStyle.doOut(elevatorTable, requestTable, id);
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
            try { sleep(1000 - (endTime - startTime)); }
            catch (InterruptedException e) { e.printStackTrace(); }
        }
        TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        elevatorTable.setLastTime(System.currentTimeMillis());
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
            elevatorTable.setLastTime(System.currentTimeMillis());
        } else {
            if (CheckStyle.needPreKickOut(elevatorTable, toFloor)) {
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
                elevatorTable.setLastTime(System.currentTimeMillis());
            }
        }
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
            if (nowTime - elevatorTable.getLastTime() < scheSpeed) {
                try { sleep(scheSpeed - (nowTime - elevatorTable.getLastTime())); }
                catch (InterruptedException e) { e.printStackTrace(); }
            }
            moveOneFloor();
            TimableOutput.println("ARRIVE-" +
                TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            elevatorTable.setLastTime(System.currentTimeMillis());
        }
    }
    
    public void updateMove(long moveSpeed) {
        if (CheckStyle.nextFloor(elevatorTable) == elevatorTable.getTransferFloor()) {
            transferFloorLock.tryOccupyTransferFloor();
        }
        boolean flag = elevatorTable.getCurrentFloor() == elevatorTable.getTransferFloor();
        long nowTime = System.currentTimeMillis();
        if (nowTime - elevatorTable.getLastTime() < moveSpeed) {
            try { sleep(moveSpeed - (nowTime - elevatorTable.getLastTime())); }
            catch (InterruptedException e) { e.printStackTrace(); }
        }
        if (Debug.debug()) {
            TimableOutput.println("[LOG] elevator-" + id + "-done-waiting-MOVE");
        }
        synchronized (elevatorTable) {
            if (CheckStyle.nextFloor(elevatorTable) == elevatorTable.getTransferFloor()) {
                moveOneFloor();
                TimableOutput.println("ARRIVE-" +
                    TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
                if (flag) {
                    transferFloorLock.releaseTransferFloor();
                }
                elevatorTable.setLastTime(System.currentTimeMillis());
            } else {
                Advice advice = strategy.getAdvice();
                if (advice == Advice.MOVE) {
                    moveOneFloor();
                    TimableOutput.println("ARRIVE-" +
                        TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
                    if (flag) {
                        transferFloorLock.releaseTransferFloor();
                    }
                    elevatorTable.setLastTime(System.currentTimeMillis());
                }
            }
        }
    }
    
    public void normalMove(long moveSpeed, boolean flag) {
        long nowTime = System.currentTimeMillis();
        if (nowTime - elevatorTable.getLastTime() < moveSpeed) {
            try { elevatorTable.wait(moveSpeed - (nowTime - elevatorTable.getLastTime())); }
            catch (InterruptedException e) { e.printStackTrace(); }
        }
        if (Debug.debug()) {
            TimableOutput.println("[LOG] elevator-" + id + "-done-waiting-MOVE");
        }
        Advice advice = strategy.getAdvice();
        if (advice == Advice.MOVE) {
            moveOneFloor();
            TimableOutput.println("ARRIVE-" +
                TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
            if (flag) {
                transferFloorLock.releaseTransferFloor();
            }
            elevatorTable.setLastTime(System.currentTimeMillis());
        } else if (advice == Advice.SCHE) {
            int toFloor = TranslateFloor.getFloorNumber(scheRequests.get(0).getToFloor());
            int curFloor = elevatorTable.getCurrentFloor();
            if (toFloor != curFloor) {
                if (elevatorTable.getDirection() == (toFloor > curFloor)) {
                    moveOneFloor();
                    TimableOutput.println("ARRIVE-" +
                        TranslateFloor.getFloorName(elevatorTable.getCurrentFloor()) + "-" + id);
                    elevatorTable.setLastTime(System.currentTimeMillis());
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
        CheckStyle.doOut(elevatorTable, requestTable, id);
        try { elevatorTable.wait(this.openSpeed); }
        catch (InterruptedException e) { e.printStackTrace(); }
        if (strategy.getAdvice() == Advice.REVERSE) {
            elevatorTable.setDirection(!elevatorTable.getDirection());//电梯转向
        }
        CheckStyle.doIn(elevatorTable, id);
        TimableOutput.println("CLOSE-" + TranslateFloor.getFloorName(currentFloor) + "-" + id);
        elevatorTable.setLastTime(System.currentTimeMillis());
    }
    
    public boolean judgeDirection(int fromFloor, int toFloor) {
        return fromFloor <= toFloor;
    }
}