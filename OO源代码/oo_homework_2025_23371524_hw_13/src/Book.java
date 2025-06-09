import com.oocourse.library1.LibraryBookId;
import com.oocourse.library1.LibraryBookIsbn;
import com.oocourse.library1.LibraryBookState;
import com.oocourse.library1.LibraryTrace;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;

public class Book extends LibraryBookId {
    private LibraryBookState curState;
    private final ArrayList<LibraryTrace> traces;
    private String appointedUser;
    private LocalDate startDate;
    
    public Book(LibraryBookIsbn isbn, String copyId) {
        super(isbn.getType(), isbn.getUid(), copyId);
        this.curState = LibraryBookState.BOOKSHELF;
        this.traces = new ArrayList<>();
        this.appointedUser = null;
        this.startDate = null;
    }
    
    public void updateState(LocalDate date, LibraryBookState nextState) {
        traces.add(new LibraryTrace(date, curState, nextState));
        curState = nextState;
    }
    
    public ArrayList<LibraryTrace> getTraces() {
        return traces;
    }
    
    public String getAppointedUser() {
        return appointedUser;
    }
    
    public void setAppointedUser(String appointedUser) {
        this.appointedUser = appointedUser;
    }
    
    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }
    
    public boolean isOutdated(LocalDate today) {
        return Math.abs(ChronoUnit.DAYS.between(startDate, today)) >= 5;
    }
}