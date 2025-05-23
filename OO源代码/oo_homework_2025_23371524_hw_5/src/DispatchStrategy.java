import com.oocourse.elevator1.PersonRequest;
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
        PersonRequest request = requestTable.getRequest();
        if (request == null) {
            return false;
        }
        Integer bestElevator = getBestEle(request);
        //没有合适的就返回null,继续递归寻找下一个，return后再把现在那个给加回去
        if (bestElevator == -1) {
            boolean isDisped = dispatch();
            requestTable.addRequest(request);
            return isDisped;
        }
        elevatorTableMap.get(bestElevator).addRequest(request);
        return true;
    }
    
    private Integer getBestEle(PersonRequest request) {
        int bestElevator = -1;
        int distElevator = request.getElevatorId();
        bestElevator = distElevator;
        return bestElevator;
    }
}
