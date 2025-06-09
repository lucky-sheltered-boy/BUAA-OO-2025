import com.oocourse.library1.LibraryBookId;
import com.oocourse.library1.LibraryBookIsbn;

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
    // studentId
    
    public BookShelf() {
        bookList = new HashMap<>();
        books = new HashMap<>();
        appointments = new ArrayList<>();
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
    
    public HashSet<Book> removeOrderBooks() {
        HashSet<Book> orderBooks = new HashSet<>();
        HashSet<Appointment> removeAppointments = new HashSet<>();
        for (Appointment appointment : appointments) {
            if (!bookList.get(appointment.getBookIsbn().toString()).isEmpty()) {
                HashSet<Book> books = bookList.get(appointment.getBookIsbn().toString());
                ArrayList<Book> bookList = new ArrayList<>(books);
                Book book = bookList.get(0);
                books.remove(book);
                book.setAppointedUser(appointment.getStudentId());
                orderBooks.add(book);
                removeAppointments.add(appointment);
            }
        }
        appointments.removeAll(removeAppointments);
        return orderBooks;
    }
}
