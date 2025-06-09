import java.time.LocalDate;
import java.util.HashSet;

public class AppointmentOffice {
    private final HashSet<Book> appointedBooks;
    
    public AppointmentOffice() {
        appointedBooks = new HashSet<>();
    }
    
    public void addBooks(HashSet<Book> books, LocalDate today) {
        appointedBooks.addAll(books);
        for (Book book : books) {
            book.setStartDate(today);
        }
    }
    
    public boolean hasOrderBook(String studentId) {
        for (Book book : appointedBooks) {
            if (book.getAppointedUser().equals(studentId)) {
                return true;
            }
        }
        return false;
    }
    
    public Book removeOrderBook(String studentId) {
        for (Book book : appointedBooks) {
            if (book.getAppointedUser().equals(studentId)) {
                appointedBooks.remove(book);
                return book;
            }
        }
        return null;
    }
    
    public HashSet<Book> removeAllOutdatedBooks(LocalDate today) {
        HashSet<Book> outdatedBooks = new HashSet<>();
        for (Book book : appointedBooks) {
            if (book.isOutdated(today)) {
                outdatedBooks.add(book);
            }
        }
        appointedBooks.removeAll(outdatedBooks);
        return outdatedBooks;
    }
    
    public HashSet<Book> getAllOutdatedBooks(LocalDate today) {
        HashSet<Book> outdatedBooks = new HashSet<>();
        for (Book book : appointedBooks) {
            if (book.isOutdated(today)) {
                outdatedBooks.add(book);
            }
        }
        return outdatedBooks;
    }
}
