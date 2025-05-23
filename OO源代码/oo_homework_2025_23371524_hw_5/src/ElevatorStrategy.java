import com.oocourse.elevator1.PersonRequest;
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
        if (canOpenForOut(curFloor) || canOpenForIn(curFloor, curNum, maxNumber, direction)) {
            return Advice.OPEN;
        }
        //如果电梯里有人
        if (curNum != 0) {
            return Advice.MOVE;
        }
        //如果电梯里没有人
        else {
            ArrayList<PersonRequest> waitingRequests = elevatorTable.getWaitingRequests();
            ArrayList<PersonRequest> insideRequests = elevatorTable.getInsideRequests();
            //如果请求队列中没有人
            if (waitingRequests.isEmpty()) {
                if (elevatorTable.isEnd() && elevatorTable.isEmpty() && insideRequests.isEmpty()) {
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
        return !elevatorTable.getToFloorRequests().get(curFloor).isEmpty();
    }
    
    public boolean canOpenForIn(int curFloor, int curNum, int maxNumber, boolean direction) {
        ArrayList<PersonRequest> fromFloorRequests =
            elevatorTable.getFromFloorRequests().get(curFloor);
        if (curNum < maxNumber && !fromFloorRequests.isEmpty()) {
            for (PersonRequest personRequest : fromFloorRequests) {
                int fromFloor = TranslateFloor.getFloorNumber(personRequest.getFromFloor());
                int toFloor = TranslateFloor.getFloorNumber(personRequest.getToFloor());
                boolean dir = judgeDirection(fromFloor, toFloor);
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
            if (curFloor == 7) {
                return false;
            }
            for (int floor = curFloor + 1; floor <= 7; floor++) {
                if (floor == 0) {
                    continue;
                }
                if (!elevatorTable.getFromFloorRequests().get(floor).isEmpty()) {
                    return true;
                }
            }
            return false;
        } else {
            if (curFloor == -4) {
                return false;
            }
            for (int floor = curFloor - 1; floor >= -4; floor--) {
                if (floor == 0) {
                    continue;
                }
                if (!elevatorTable.getFromFloorRequests().get(floor).isEmpty()) {
                    return true;
                }
            }
            return false;
        }
    }
}
