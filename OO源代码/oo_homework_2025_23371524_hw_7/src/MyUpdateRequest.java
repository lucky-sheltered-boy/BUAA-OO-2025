import com.oocourse.elevator3.UpdateRequest;

public class MyUpdateRequest extends UpdateRequest {
    private UpdateLock updateLock;
    private TransferFloorLock transferFloorLock;
    
    public MyUpdateRequest(int elevatorId1, int elevatorId2, String transferFloor,
        UpdateLock updateLock, TransferFloorLock transferFloorLock) {
        super(elevatorId1, elevatorId2, transferFloor);
        this.updateLock = updateLock;
        this.transferFloorLock = transferFloorLock;
    }
    
    public UpdateLock getUpdateLock() {
        return updateLock;
    }
    
    public TransferFloorLock getTransferFloorLock() {
        return transferFloorLock;
    }
}
