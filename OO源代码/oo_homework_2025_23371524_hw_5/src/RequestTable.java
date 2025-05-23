import com.oocourse.elevator1.PersonRequest;
import java.util.ArrayList;
//import java.util.HashMap;

public class RequestTable {
    private boolean endFlag;
    private ArrayList<PersonRequest> requestList;
    
    public RequestTable() {
        endFlag = false;
        requestList = new ArrayList<>();
    }
    
    public synchronized void addRequest(PersonRequest request) {
        requestList.add(request);
        this.notifyAll();
    }
    
    public synchronized PersonRequest getRequest() {
        while (requestList.isEmpty() && !this.endFlag) {
            try {
                this.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        if (requestList.isEmpty()) {
            return null;
        }
        return requestList.remove(0);
    }
    
    public synchronized void setEndFlag() {
        this.notifyAll();
        endFlag = true;
    }
    
    public synchronized boolean isOver() {
        return this.endFlag && requestList.isEmpty();
    }
}
