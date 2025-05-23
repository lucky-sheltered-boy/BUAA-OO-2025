import com.oocourse.elevator3.Request;
import com.oocourse.elevator3.ScheRequest;

import java.util.ArrayList;

public class RequestTable {
    private boolean endFlag;
    private ArrayList<MyPersonRequest> myPersonRequestList;
    private ArrayList<ScheRequest> scheRequestList;
    private ArrayList<MyUpdateRequest> myUpdateRequestList;
    private int requestCount = 0;
    private boolean returnNullFlag = false;
    
    public RequestTable() {
        endFlag = false;
        myPersonRequestList = new ArrayList<>();
        scheRequestList = new ArrayList<>();
        myUpdateRequestList = new ArrayList<>();
    }
    
    public synchronized void addRequest(Request request) {
        if (request instanceof MyPersonRequest) {
            myPersonRequestList.add((MyPersonRequest) request);
        } else if (request instanceof ScheRequest) {
            scheRequestList.add((ScheRequest) request);
        } else if (request instanceof MyUpdateRequest) {
            myUpdateRequestList.add((MyUpdateRequest) request);
        }
        this.notifyAll();
    }
    
    public synchronized Request getRequest() {
        while (scheRequestList.isEmpty() && myPersonRequestList.isEmpty() &&
            myUpdateRequestList.isEmpty() && !isOver() && !returnNullFlag) {
            try {
                this.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        if (!scheRequestList.isEmpty()) {
            return scheRequestList.remove(0);
        } else if (!myUpdateRequestList.isEmpty()) {
            return myUpdateRequestList.remove(0);
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
    
    public synchronized void countPlus(int count) {
        requestCount += count;
    }
    
    public synchronized void countMinus() {
        requestCount--;
        if (requestCount == 0) {
            this.notifyAll();
        }
    }
    
    public synchronized boolean isOver() {
        return endFlag && myPersonRequestList.isEmpty() &&
            scheRequestList.isEmpty() &&
            myUpdateRequestList.isEmpty() &&
            requestCount == 0;
    }
    
    public synchronized void setReturnNullFlag(boolean flag) {
        returnNullFlag = flag;
    }
}
