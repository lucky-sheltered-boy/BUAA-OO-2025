import com.oocourse.elevator2.Request;
import com.oocourse.elevator2.ScheRequest;

import java.util.ArrayList;

public class RequestTable {
    private boolean endFlag;
    private ArrayList<MyPersonRequest> myPersonRequestList;
    private ArrayList<ScheRequest> scheRequestList;
    private int requestCount = 0;
    private boolean returnNullFlag = false;
    
    public RequestTable() {
        endFlag = false;
        myPersonRequestList = new ArrayList<>();
        scheRequestList = new ArrayList<>();
    }
    
    public synchronized void addRequest(Request request) {
        if (request instanceof MyPersonRequest) {
            myPersonRequestList.add((MyPersonRequest) request);
        } else if (request instanceof ScheRequest) {
            scheRequestList.add((ScheRequest) request);
        }
        this.notifyAll();
    }
    
    public synchronized Request getRequest() {
        while (scheRequestList.isEmpty() && myPersonRequestList.isEmpty()
            && !isOver() && !returnNullFlag) {
            try {
                this.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        if (!scheRequestList.isEmpty()) {
            return scheRequestList.remove(0);
        } else if (!myPersonRequestList.isEmpty()) {
            return myPersonRequestList.remove(0);
        } else {
            return null;
        }
    }
    
    public synchronized void setEndFlag() {
        this.notifyAll();
        endFlag = true;
    }
    
    public synchronized void countPlus() {
        requestCount++;
    }
    
    public synchronized void countMinus() {
        requestCount--;
        if (requestCount == 0) {
            this.notifyAll();
        }
    }
    
    public synchronized boolean isOver() {
        return endFlag && myPersonRequestList.isEmpty() &&
            scheRequestList.isEmpty() && requestCount == 0;
    }
    
    public synchronized void setReturnNullFlag(boolean flag) {
        returnNullFlag = flag;
    }
}
