import com.oocourse.library3.LibraryBookIsbn;

public class Appointment {
    private String studentId;
    private LibraryBookIsbn isbn;
    
    public Appointment(String studentId, LibraryBookIsbn isbn) {
        this.studentId = studentId;
        this.isbn = isbn;
    }
    
    public String getStudentId() {
        return studentId;
    }
    
    public LibraryBookIsbn getBookIsbn() {
        return isbn;
    }
}
