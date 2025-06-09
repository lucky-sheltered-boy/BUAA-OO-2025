import java.util.HashMap;
import java.util.HashSet;

public class ReadingRoom {
    private final HashMap<String, Book> readingBooks;
    
    public ReadingRoom() {
        readingBooks = new HashMap<>();
    }
    
    public boolean hasUnreturnedBook(String studentId) {
        return readingBooks.containsKey(studentId);
    }
    
    public void addBook(String studentId, Book book) {
        readingBooks.put(studentId, book);
    }
    
    public Book removeBook(String studentId) {
        if (hasUnreturnedBook(studentId)) {
            return readingBooks.remove(studentId);
        }
        return null;
    }
    
    public HashSet<Book> removeAllBooks() {
        HashSet<Book> temp = new HashSet<>(readingBooks.values());
        readingBooks.clear();
        return temp;
    }
}
