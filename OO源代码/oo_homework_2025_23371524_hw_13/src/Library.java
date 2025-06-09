import com.oocourse.library1.LibraryBookId;
import com.oocourse.library1.LibraryBookIsbn;
import com.oocourse.library1.LibraryBookState;
import com.oocourse.library1.LibraryCommand;
import com.oocourse.library1.LibraryMoveInfo;

import static com.oocourse.library1.LibraryIO.PRINTER;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;

public class Library {
    private final BookShelf bookshelf;
    private final AppointmentOffice appointmentOffice;
    private final BorrowReturnOffice borrowReturnOffice;
    private final UserTable userTable;
    
    public Library(Map<LibraryBookIsbn, Integer> bookList) {
        bookshelf = new BookShelf();
        appointmentOffice = new AppointmentOffice();
        borrowReturnOffice = new BorrowReturnOffice();
        userTable = new UserTable();
        bookshelf.init(bookList);
    }
    
    public void userBorrowBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!bookshelf.hasSpareBook(isbn) || !userTable.userCanHoldBook(studentId, isbn)) {
            PRINTER.reject(req);
        } else {
            Book book = bookshelf.removeBook(isbn);
            userTable.addBook2User(studentId, book);
            book.updateState(req.getDate(), LibraryBookState.USER);
            PRINTER.accept(req, book);
        }
    }
    
    public void userQueryBook(LibraryBookId bookId, LocalDate today) {
        PRINTER.info(today, bookId, bookshelf.getBook(bookId).getTraces());
    }
    
    public void userReturnBook(LibraryBookId bookId, String studentId, LibraryCommand req) {
        Book book = userTable.removeBook(studentId, bookId);
        borrowReturnOffice.addBook(book);
        book.updateState(req.getDate(), LibraryBookState.BORROW_RETURN_OFFICE);
        PRINTER.accept(req);
    }
    
    public void userOrderBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!userTable.userCanHoldBook(studentId, isbn) ||
            userTable.userHasUnhandledOrder(studentId)) {
            PRINTER.reject(req);
        } else {
            bookshelf.addAppointment(new Appointment(studentId, isbn));
            userTable.addOrder(studentId);
            PRINTER.accept(req);
        }
    }
    
    public void userPickBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!appointmentOffice.hasOrderBook(studentId) ||
            !userTable.userCanHoldBook(studentId, isbn)) {
            PRINTER.reject(req);
        } else {
            Book book = appointmentOffice.removeOrderBook(studentId);
            userTable.addBook2User(studentId, book);
            book.updateState(req.getDate(), LibraryBookState.USER);
            userTable.removeOrder(studentId);
            PRINTER.accept(req, book);
        }
    }
    
    public void open(LocalDate today) {
        ArrayList<LibraryMoveInfo> moveInfos = new ArrayList<>();
        HashSet<Book> returnedBooks = borrowReturnOffice.removeAllBooks();
        bookshelf.addBooks(returnedBooks);
        for (Book book : returnedBooks) {
            book.updateState(today, LibraryBookState.BOOKSHELF);
            moveInfos.add(new LibraryMoveInfo(book, "bro", "bs"));
        }
        // return_book -> bookshelf
        HashSet<Book> outdatedBooks = appointmentOffice.removeAllOutdatedBooks(today);
        bookshelf.addBooks(outdatedBooks);
        for (Book book : outdatedBooks) {
            userTable.removeOrder(book.getAppointedUser());
            book.updateState(today, LibraryBookState.BOOKSHELF);
            moveInfos.add(new LibraryMoveInfo(book, "ao", "bs"));
        }
        // outdated_book -> bookshelf
        HashSet<Book> orderBooks = bookshelf.removeOrderBooks();
        appointmentOffice.addBooks(orderBooks, today);
        for (Book book : orderBooks) {
            book.updateState(today, LibraryBookState.APPOINTMENT_OFFICE);
            moveInfos.add(new LibraryMoveInfo(book, "bs", "ao", book.getAppointedUser()));
        }
        // order_book -> appointment_office
        PRINTER.move(today, moveInfos);
    }
    
    public void close(LocalDate today) {
        PRINTER.move(today);
    }
}
