import com.oocourse.library2.LibraryBookIsbn;
import com.oocourse.library2.LibraryBookId;
import com.oocourse.library2.LibraryBookState;
import com.oocourse.library2.LibraryMoveInfo;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class BookShelf {
    private final HashMap<String, Book> books;
    // id_string -> book
    // global books
    private final HashMap<String, HashSet<Book>> bookList;
    // isbn_string -> book_copy
    // temporary books
    private final ArrayList<Appointment> appointments;
    // studentId && isbn
    private final HashSet<Book> hotBooks;
    
    public BookShelf() {
        bookList = new HashMap<>();
        books = new HashMap<>();
        appointments = new ArrayList<>();
        hotBooks = new HashSet<>();
    }
    
    public void init(Map<LibraryBookIsbn, Integer> bookList) {
        for (LibraryBookIsbn isbn : bookList.keySet()) {
            HashSet<Book> books = new HashSet<>();
            for (int i = 1; i <= bookList.get(isbn); i++) {
                Book book = null;
                if (i < 10) {
                    book = new Book(isbn, "0" + i);
                } else {
                    book = new Book(isbn, String.valueOf(i));
                }
                books.add(book);
                this.books.put(book.toString(), book);
            }
            this.bookList.put(isbn.toString(), books);
        }
    }
    
    public boolean hasSpareBook(LibraryBookIsbn isbn) {
        if (bookList.containsKey(isbn.toString())) {
            return !bookList.get(isbn.toString()).isEmpty();
        }
        return false;
    }
    
    public Book removeBook(LibraryBookIsbn isbn) {
        if (hasSpareBook(isbn)) {
            HashSet<Book> books = bookList.get(isbn.toString());
            ArrayList<Book> bookList = new ArrayList<>(books);
            Book book = bookList.get(0);
            books.remove(book);
            if (book.isAtHotBookShelf()) {
                hotBooks.remove(book);
            }
            return book;
        }
        return null;
    }
    
    public Book getBook(LibraryBookId bookId) {
        if (books.containsKey(bookId.toString())) {
            return books.get(bookId.toString());
        }
        return null;
    }
    
    public void addBook(Book book) {
        bookList.get(book.getBookIsbn().toString()).add(book);
    }
    
    public void addAppointment(Appointment appointment) {
        appointments.add(appointment);
    }
    
    public void addBooks(HashSet<Book> books) {
        for (Book book : books) {
            addBook(book);
        }
    }
    
    public HashSet<Book> removeOrderBooks(ArrayList<LibraryMoveInfo> moveInfos) {
        HashSet<Book> orderBooks = new HashSet<>();
        HashSet<Appointment> removeAppointments = new HashSet<>();
        for (Appointment appointment : appointments) {
            if (!bookList.get(appointment.getBookIsbn().toString()).isEmpty()) {
                HashSet<Book> books = bookList.get(appointment.getBookIsbn().toString());
                ArrayList<Book> bookList = new ArrayList<>(books);
                Book book = bookList.get(0);
                book.setAppointedUser(appointment.getStudentId());
                if (book.isAtHotBookShelf()) {
                    hotBooks.remove(book);
                    moveInfos.add(new LibraryMoveInfo(book, "hbs", "ao", book.getAppointedUser()));
                } else {
                    moveInfos.add(new LibraryMoveInfo(book, "bs", "ao", book.getAppointedUser()));
                }
                books.remove(book);
                orderBooks.add(book);
                removeAppointments.add(appointment);
            }
        }
        appointments.removeAll(removeAppointments);
        return orderBooks;
    }
    
    public void moveHotBooks(HashSet<LibraryBookIsbn> hotBooks,
        LocalDate today, ArrayList<LibraryMoveInfo> moveInfos) {
        for (Book book : this.hotBooks) {
            book.updateState(today, LibraryBookState.BOOKSHELF);
            moveInfos.add(new LibraryMoveInfo(book, "hbs", "bs"));
        }
        this.hotBooks.clear();
        for (LibraryBookIsbn isbn : hotBooks) {
            HashSet<Book> books = bookList.get(isbn.toString());
            for (Book book : books) {
                book.updateState(today, LibraryBookState.HOT_BOOKSHELF);
                moveInfos.add(new LibraryMoveInfo(book, "bs", "hbs"));
                this.hotBooks.add(book);
            }
        }
    }
}
