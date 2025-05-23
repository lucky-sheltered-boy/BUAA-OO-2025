import java.util.ArrayList;

public class ElevatorStrategy {
    private ElevatorTable elevatorTable;
    
    public ElevatorStrategy(ElevatorTable elevatorTable) {
        this.elevatorTable = elevatorTable;
    }
    
    public Advice getAdvice() {
        int curFloor = elevatorTable.getCurrentFloor();
        int curNum = elevatorTable.getCurrentNum();
        boolean direction = elevatorTable.getDirection();
        int maxNumber = elevatorTable.getMaxNumber();
        if (!elevatorTable.getScheRequests().isEmpty()) {
            return Advice.SCHE;
        }
        if (!elevatorTable.getMyUpdateRequests().isEmpty()) {
            return Advice.UPDATE;
        }
        if (canOpenForOut(curFloor) || canOpenForIn(curFloor, curNum, maxNumber, direction)) {
            return Advice.OPEN;
        }
        //如果电梯里有人
        if (curNum != 0) {
            return Advice.MOVE;
        }
        //如果电梯里没有人
        else {
            ArrayList<MyPersonRequest> waitingRequests = elevatorTable.getWaitingRequests();
            ArrayList<MyPersonRequest> insideRequests = elevatorTable.getInsideRequests();
            //如果请求队列中没有人
            if (waitingRequests.isEmpty()) {
                if (elevatorTable.isEnd() && insideRequests.isEmpty()) {
                    return Advice.OVER; //如果输入结束，电梯线程结束
                } else {
                    return Advice.WAIT; //如果输入未结束，电梯线程等待
                }
            }
            //如果请求队列中有人
            if (hasReqInOriginDirection(curFloor, direction)) {
                return Advice.MOVE; //如果有请求发出地在电梯“前方”，则前当前方向移动一层
            } else {
                return Advice.REVERSE; //否则，电梯转向（仅状态改变，电梯不移动）
            }
        }
    }
    
    public boolean canOpenForOut(int curFloor) {
        if (!elevatorTable.getToFloorRequests().get(curFloor).isEmpty()) {
            return true;
        } else {
            if (elevatorTable.isUpdated() &&
                elevatorTable.getCurrentFloor() == elevatorTable.getTransferFloor()) {
                for (MyPersonRequest myPersonRequest : elevatorTable.getInsideRequests()) {
                    if (elevatorTable.isToFloorNotQualified(myPersonRequest) == 1) {
                        return true;
                    }
                }
            }
            return false;
        }
    }
    
    public boolean canOpenForIn(int curFloor, int curNum, int maxNumber, boolean direction) {
        ArrayList<MyPersonRequest> fromFloorRequests =
            elevatorTable.getFromFloorRequests().get(curFloor);
        if (curNum < maxNumber && !fromFloorRequests.isEmpty()) {
            for (MyPersonRequest myPersonRequest : fromFloorRequests) {
                int currentFloor = TranslateFloor.getFloorNumber(myPersonRequest.getCurrentFloor());
                int toFloor = TranslateFloor.getFloorNumber(myPersonRequest.getToFloor());
                boolean dir = judgeDirection(currentFloor, toFloor);
                if (dir == direction) {
                    return true;
                }
            }
            return false;
        } else {
            return false;
        }
    }
    
    public boolean judgeDirection(int fromFloor, int toFloor) {
        return fromFloor <= toFloor;
    }
    
    public boolean hasReqInOriginDirection(int curFloor, boolean direction) {
        if (direction) {
            int topFloor = elevatorTable.getTopFloor();
            for (int floor = curFloor + 1; floor <= topFloor; floor++) {
                if (!elevatorTable.getFromFloorRequests().get(floor).isEmpty()) {
                    return true;
                }
            }
            return false;
        } else {
            int bottomFloor = elevatorTable.getBottomFloor();
            for (int floor = curFloor - 1; floor >= bottomFloor; floor--) {
                if (!elevatorTable.getFromFloorRequests().get(floor).isEmpty()) {
                    return true;
                }
            }
            return false;
        }
    }
}
