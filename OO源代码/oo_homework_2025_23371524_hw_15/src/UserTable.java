import com.oocourse.library3.LibraryBookId;
import com.oocourse.library3.LibraryBookIsbn;
import java.util.HashMap;
import java.util.HashSet;

public class UserTable {
    private final HashMap<String, HashSet<Book>> userListB;
    // studentId -> book
    private final HashMap<String, HashMap<String, HashSet<Book>>> userListC;
    // studentId -> isbn_string -> book_copy
    private final HashMap<String, Boolean> userOrder;
    // studentId -> true/false
    private final HashMap<String, Integer> userCredit;
    // studentId -> credit
    
    public UserTable() {
        userListB = new HashMap<>();
        userListC = new HashMap<>();
        userOrder = new HashMap<>();
        userCredit = new HashMap<>();
    }
    
    public boolean hasUser(String studentId) {
        return userListB.containsKey(studentId);
    }
    
    public void addUser(String studentId) {
        if (!hasUser(studentId)) {
            userListB.put(studentId, new HashSet<>());
            userListC.put(studentId, new HashMap<>());
            userOrder.put(studentId, false);
            userCredit.put(studentId, 100);
        }
    }
    
    public void addBook2User(String studentId, Book book) {
        if (!hasUser(studentId)) {
            addUser(studentId);
        }
        if (book.isTypeB()) {
            userListB.get(studentId).add(book);
        } else if (book.isTypeC()) {
            String isbn = book.getBookIsbn().toString();
            if (!userListC.get(studentId).containsKey(isbn)) {
                userListC.get(studentId).put(isbn, new HashSet<>());
            }
            userListC.get(studentId).get(isbn).add(book);
        }
    }
    
    public boolean userCanHoldBook(String studentId, LibraryBookIsbn isbn) {
        if (isbn.isTypeA()) {
            return false;
        }
        if (!hasUser(studentId)) {
            return true;
        }
        if (isbn.isTypeB()) {
            return userListB.get(studentId).isEmpty();
        }
        if (isbn.isTypeC()) {
            if (!userListC.get(studentId).containsKey(isbn.toString())) {
                return true;
            }
            return userListC.get(studentId).get(isbn.toString()).isEmpty();
        }
        return false;
    }
    
    public Book removeBook(String studentId, LibraryBookId bookId) {
        if (!hasUser(studentId)) {
            return null;
        }
        if (bookId.isTypeB()) {
            if (userListB.get(studentId).size() == 1) {
                Book book = userListB.get(studentId).iterator().next();
                userListB.get(studentId).remove(book);
                return book;
            } else {
                return null;
            }
        } else if (bookId.isTypeC()) {
            String isbn = bookId.getBookIsbn().toString();
            if (userListC.get(studentId).containsKey(isbn)) {
                HashSet<Book> books = userListC.get(studentId).get(isbn);
                if (books.size() == 1) {
                    Book book = books.iterator().next();
                    books.remove(book);
                    return book;
                } else {
                    return null;
                }
            }
            return null;
        } else {
            return null;
        }
    }
    
    public boolean userHasUnhandledOrder(String studentId) {
        if (!hasUser(studentId)) {
            return false;
        }
        return userOrder.get(studentId);
    }
    
    public void addOrder(String studentId) {
        if (!hasUser(studentId)) {
            addUser(studentId);
        }
        userOrder.put(studentId, true);
    }
    
    public void removeOrder(String studentId) {
        if (!hasUser(studentId)) {
            return;
        }
        userOrder.put(studentId, false);
    }
    
    public void addCredit(String studentId, int credit) {
        if (!hasUser(studentId)) {
            addUser(studentId);
        }
        int curCredit = userCredit.get(studentId);
        int newCredit;
        if (curCredit + credit > 180) {
            newCredit = 180;
        } else if (curCredit + credit < 0) {
            newCredit = 0;
        } else {
            newCredit = curCredit + credit;
        }
        userCredit.put(studentId, newCredit);
    }
    
    public int getCredit(String studentId) {
        if (!hasUser(studentId)) {
            return 100;
        }
        return userCredit.get(studentId);
    }
    
    public boolean creditAllowRead(String studentId, LibraryBookIsbn isbn) {
        if (!hasUser(studentId)) {
            return true;
        }
        int credit = userCredit.get(studentId);
        if (isbn.isTypeA()) {
            return credit >= 40;
        } else if (isbn.isTypeB() || isbn.isTypeC()) {
            return credit > 0;
        }
        return false;
    }
    
    public boolean creditAllowBorrow(String studentId, LibraryBookIsbn isbn) {
        if (!hasUser(studentId)) {
            return true;
        }
        int credit = userCredit.get(studentId);
        if (isbn.isTypeA()) {
            return false;
        } else if (isbn.isTypeB() || isbn.isTypeC()) {
            return credit >= 60;
        }
        return false;
    }
    
    public boolean creditAllowOrder(String studentId, LibraryBookIsbn isbn) {
        if (!hasUser(studentId)) {
            return true;
        }
        int credit = userCredit.get(studentId);
        if (isbn.isTypeA()) {
            return false;
        } else if (isbn.isTypeB() || isbn.isTypeC()) {
            return credit >= 100;
        }
        return false;
    }
}
