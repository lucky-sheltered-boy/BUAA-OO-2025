import com.oocourse.library3.LibraryBookId;
import com.oocourse.library3.LibraryBookIsbn;
import com.oocourse.library3.LibraryBookState;
import com.oocourse.library3.LibraryTrace;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;

import static java.lang.Math.abs;

public class Book extends LibraryBookId {
    private LibraryBookState curState;
    private final ArrayList<LibraryTrace> traces;
    private String appointedUser;
    private LocalDate startDate;
    private LocalDate dueDate;
    private LocalDate subDate;
    private boolean isSubtracted;
    private boolean isSubtracted4Outdated;
    
    public Book(LibraryBookIsbn isbn, String copyId) {
        super(isbn.getType(), isbn.getUid(), copyId);
        this.curState = LibraryBookState.BOOKSHELF;
        this.traces = new ArrayList<>();
        this.appointedUser = null;
        this.startDate = null;
        this.dueDate = null;
        this.subDate = null;
        this.isSubtracted = false;
        this.isSubtracted4Outdated = false;
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
        return abs(ChronoUnit.DAYS.between(startDate, today)) >= 5;
    }
    
    public boolean isAtHotBookShelf() {
        return curState == LibraryBookState.HOT_BOOKSHELF;
    }
    
    public void setDueDate(LocalDate today) {
        if (isTypeB()) {
            dueDate = today.plusDays(30);
        } else if (isTypeC()) {
            dueDate = today.plusDays(60);
        }
        subDate = dueDate.plusDays(1);
        isSubtracted = false;
    }
    
    public boolean isOverdue(LocalDate today) {
        if (dueDate == null) {
            return false;
        }
        return today.isAfter(dueDate);
    }
    
    public int calculateSubCredit(LocalDate today) {
        int subCredit = 0;
        if (!isSubtracted) {
            subCredit += 5;
            isSubtracted = true;
        }
        subCredit += 5 * (int) abs(ChronoUnit.DAYS.between(subDate, today));
        subDate = today;
        return subCredit;
    }
    
    public boolean isSubtracted4Outdated() {
        return isSubtracted4Outdated;
    }
    
    public void setSubtracted4Outdated(boolean subtracted4Outdated) {
        isSubtracted4Outdated = subtracted4Outdated;
    }
}