import com.oocourse.elevator3.PersonRequest;

public class MyPersonRequest extends PersonRequest {
    private String currentFloor;
    
    public MyPersonRequest(String fromFloor, String toFloor, int personId, int priority) {
        super(fromFloor, toFloor, personId, priority);
        this.currentFloor = fromFloor;
    }
    
    public String getCurrentFloor() {
        return currentFloor;
    }
    
    public void setCurrentFloor(String currentFloor) {
        this.currentFloor = currentFloor;
    }
    
    public boolean getDirection() {
        return TranslateFloor.getFloorNumber(getToFloor()) >=
            TranslateFloor.getFloorNumber(getCurrentFloor());
    }
}
