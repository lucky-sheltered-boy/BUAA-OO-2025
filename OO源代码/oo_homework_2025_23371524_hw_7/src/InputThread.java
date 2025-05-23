import com.oocourse.elevator3.UpdateRequest;
import com.oocourse.elevator3.ElevatorInput;
import com.oocourse.elevator3.PersonRequest;
import com.oocourse.elevator3.Request;
import com.oocourse.elevator3.ScheRequest;

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
                    requestTable.countPlus();
                    requestTable.addRequest(myPersonRequest);
                } else if (request instanceof ScheRequest) {
                    ScheRequest scheRequest = (ScheRequest) request;
                    requestTable.countPlus();
                    requestTable.addRequest(scheRequest);
                } else if (request instanceof UpdateRequest) {
                    TransferFloorLock transferFloorLock = new TransferFloorLock();
                    UpdateLock updateLock = new UpdateLock((UpdateRequest) request,
                        transferFloorLock);
                    updateLock.start();
                    MyUpdateRequest myUpdateRequest = new MyUpdateRequest(
                        ((UpdateRequest) request).getElevatorAId(),
                        ((UpdateRequest) request).getElevatorBId(),
                        ((UpdateRequest) request).getTransferFloor(),
                        updateLock, transferFloorLock);
                    requestTable.countPlus(2);
                    requestTable.addRequest(myUpdateRequest);
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
