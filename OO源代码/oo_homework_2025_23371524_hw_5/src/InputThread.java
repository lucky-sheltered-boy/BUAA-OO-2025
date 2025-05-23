import com.oocourse.elevator1.ElevatorInput;
import com.oocourse.elevator1.PersonRequest;
import com.oocourse.elevator1.Request;
//import com.oocourse.elevator1.TimableOutput;

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
                //TimableOutput.println("end");
                break;
            } else {
                if (request instanceof PersonRequest) {
                    PersonRequest personRequest = (PersonRequest) request;
                    requestTable.addRequest(personRequest);
                    //TimableOutput.println("add " + personRequest);
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
