import java.util.HashSet;

public class BorrowReturnOffice {
    private final HashSet<Book> books;
    
    public BorrowReturnOffice() {
        books = new HashSet<Book>();
    }
    
    public void addBook(Book book) {
        books.add(book);
    }
    
    public HashSet<Book> removeAllBooks() {
        HashSet<Book> temp = new HashSet<Book>(books);
        books.clear();
        return temp;
    }
}
