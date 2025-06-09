import com.oocourse.library3.LibraryBookIsbn;
import com.oocourse.library3.LibraryBookId;
import com.oocourse.library3.LibraryBookState;
import com.oocourse.library3.LibraryCommand;
import com.oocourse.library3.LibraryMoveInfo;
import com.oocourse.library3.LibraryQcsCmd;
import com.oocourse.library3.annotation.SendMessage;
import com.oocourse.library3.annotation.Trigger;

import static com.oocourse.library3.LibraryIO.PRINTER;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class Library {
    private final BookShelf bookshelf;
    private final AppointmentOffice appointmentOffice;
    private final BorrowReturnOffice borrowReturnOffice;
    private final UserTable userTable;
    private final ReadingRoom readingRoom;
    private final HashSet<LibraryBookIsbn> hotBooks;
    private final HashMap<Book, String> userHoldBooks;
    
    public Library(Map<LibraryBookIsbn, Integer> bookList) {
        bookshelf = new BookShelf();
        appointmentOffice = new AppointmentOffice();
        borrowReturnOffice = new BorrowReturnOffice();
        userTable = new UserTable();
        readingRoom = new ReadingRoom();
        hotBooks = new HashSet<>();
        bookshelf.init(bookList);
        userHoldBooks = new HashMap<>();
    }
    
    public void userBorrowBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!bookshelf.hasSpareBook(isbn) || !userTable.userCanHoldBook(studentId, isbn)
            || !userTable.creditAllowBorrow(studentId, isbn)) {
            PRINTER.reject(req);
        } else {
            Book book = bookshelf.removeBook(isbn);
            userTable.addBook2User(studentId, book);
            book.updateState(req.getDate(), LibraryBookState.USER);
            LocalDate today = req.getDate();
            book.setDueDate(today);
            userHoldBooks.put(book, studentId);
            hotBooks.add(isbn);
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
        userHoldBooks.remove(book);
        if (!book.isOverdue(req.getDate())) {
            userTable.addCredit(studentId, 10);
            PRINTER.accept(req, "not overdue");
        } else {
            PRINTER.accept(req, "overdue");
        }
    }
    
    public void userOrderBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!userTable.userCanHoldBook(studentId, isbn) ||
            userTable.userHasUnhandledOrder(studentId) ||
            !userTable.creditAllowOrder(studentId, isbn)) {
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
            book.setDueDate(req.getDate());
            userHoldBooks.put(book, studentId);
            userTable.removeOrder(studentId);
            PRINTER.accept(req, book);
        }
    }
    
    @Trigger(from = "Close", to = "Open")
    public void open(LocalDate today) {
        adjustCredit(today);
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
        
        HashSet<Book> readingBooks = readingRoom.removeAllBooks();
        bookshelf.addBooks(readingBooks);
        for (Book book : readingBooks) {
            book.updateState(today, LibraryBookState.BOOKSHELF);
            moveInfos.add(new LibraryMoveInfo(book, "rr", "bs"));
        }
        // reading_book -> bookshelf
        
        HashSet<Book> orderBooks = bookshelf.removeOrderBooks(moveInfos);
        appointmentOffice.addBooks(orderBooks, today);
        for (Book book : orderBooks) {
            book.updateState(today, LibraryBookState.APPOINTMENT_OFFICE);
        }
        // order_book -> appointment_office
        
        bookshelf.moveHotBooks(hotBooks, today, moveInfos);
        // hot_books <-> bookshelf
        hotBooks.clear();
        
        PRINTER.move(today, moveInfos);
    }
    
    public void adjustCredit(LocalDate today) {
        for (Book book : userHoldBooks.keySet()) {
            if (book.isOverdue(today)) {
                userTable.addCredit(userHoldBooks.get(book), -book.calculateSubCredit(today));
            }
        }
        HashSet<String> unreturnedReaders = readingRoom.getUnreturnedReaders();
        for (String reader : unreturnedReaders) {
            userTable.addCredit(reader, -10);
        }
        HashSet<Book> outdatedBooks = appointmentOffice.getAllOutdatedBooks(today);
        for (Book book : outdatedBooks) {
            if (!book.isSubtracted4Outdated()) {
                userTable.addCredit(book.getAppointedUser(), -15);
                book.setSubtracted4Outdated(true);
            }
        }
    }
    
    @Trigger(from = "Open", to = "Close")
    public void close(LocalDate today) {
        PRINTER.move(today);
    }
    
    public void userReadBook(LibraryBookIsbn isbn, String studentId, LibraryCommand req) {
        if (!bookshelf.hasSpareBook(isbn) || readingRoom.hasUnreturnedBook(studentId)
            || !userTable.creditAllowRead(studentId, isbn)) {
            PRINTER.reject(req);
        } else {
            Book book = bookshelf.removeBook(isbn);
            book.updateState(req.getDate(), LibraryBookState.READING_ROOM);
            readingRoom.addBook(studentId, book);
            hotBooks.add(isbn);
            PRINTER.accept(req, book);
        }
    }
    
    public void userRestoreBook(LibraryBookId bookId, String studentId, LibraryCommand req) {
        Book book = readingRoom.removeBook(studentId);
        book.updateState(req.getDate(), LibraryBookState.BORROW_RETURN_OFFICE);
        borrowReturnOffice.addBook(book);
        userTable.addCredit(studentId, 10);
        PRINTER.accept(req);
    }
    
    public void queryCreditScore(LocalDate today, LibraryCommand req) {
        String studentId = ((LibraryQcsCmd)req).getStudentId();
        if (userTable.hasUser(studentId)) {
            int creditScore = userTable.getCredit(studentId);
            PRINTER.info(today, studentId, creditScore);
        } else {
            PRINTER.info(today, studentId, 100);
        }
    }
    
    @SendMessage(from = "obj:Library", to = "obj:AppointmentOffice")
    public void orderNewBook() {
        // do nothing
    }
    
    @SendMessage(from = "obj:Library", to = "obj:AppointmentOffice")
    public void orderAgain() {
        // do nothing
    }
}
