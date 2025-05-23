import com.oocourse.elevator3.TimableOutput;
import com.oocourse.elevator3.UpdateRequest;

public class UpdateLock extends Thread {
    private TransferFloorLock transferFloorLock;
    
    private int idA;
    private int idB;
    private int numOfReadyEle = 0;
    
    public UpdateLock(UpdateRequest updateRequest, TransferFloorLock transferFloorLock) {
        this.idA = updateRequest.getElevatorAId();
        this.idB = updateRequest.getElevatorBId();
        this.transferFloorLock = transferFloorLock;
    }
    
    public synchronized void plusNumOfReadyEle() {
        numOfReadyEle++;
        this.notifyAll();
    }
    
    @Override
    public void run() {
        synchronized (this) {
            while (numOfReadyEle < 2) {
                try {
                    this.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
        TimableOutput.println("UPDATE-BEGIN-" + idA + "-" + idB);
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        TimableOutput.println("UPDATE-END-" + idA + "-" + idB);
        synchronized (transferFloorLock) {
            transferFloorLock.notifyAll();
        }
    }
}
