import com.oocourse.elevator2.ElevatorInput;
import com.oocourse.elevator2.PersonRequest;
import com.oocourse.elevator2.Request;
import com.oocourse.elevator2.ScheRequest;

import java.io.IOException;

public class InputThread extends Thread {
    private RequestTable requestTable;
    
    public InputThread(RequestTable requestTable) {
        this.requestTable = requestTable;
    }
    
    @Override
    public void run() {
        ElevatorInput elevatorInput = new ElevatorInput(System.in);
        while (true) {
            Request request = elevatorInput.nextRequest();
            if (request == null) {
                requestTable.setEndFlag();
                break;
            } else {
                if (request instanceof PersonRequest) {
                    PersonRequest personRequest = (PersonRequest) request;
                    MyPersonRequest myPersonRequest = new MyPersonRequest(
                        personRequest.getFromFloor(), personRequest.getToFloor(),
                        personRequest.getPersonId(), personRequest.getPriority());
                    requestTable.addRequest(myPersonRequest);
                    requestTable.countPlus();
                } else if (request instanceof ScheRequest) {
                    ScheRequest scheRequest = (ScheRequest) request;
                    requestTable.addRequest(scheRequest);
                    requestTable.countPlus();
                }
            }
        }
        try {
            elevatorInput.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
