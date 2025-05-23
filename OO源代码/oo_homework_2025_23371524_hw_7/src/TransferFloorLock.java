public class TransferFloorLock {
    private boolean isOccupied = false;
    
    public TransferFloorLock() {
    }
    
    public void tryOccupyTransferFloor() {
        synchronized (this) {
            while (isOccupied) {
                try {
                    this.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            occupyTransferFloor();
        }
    }
    
    public synchronized void occupyTransferFloor() {
        isOccupied = true;
    }
    
    public synchronized void releaseTransferFloor() {
        isOccupied = false;
        this.notifyAll();
    }
}
