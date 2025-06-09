import com.oocourse.library2.LibraryBookIsbn;
import com.oocourse.library2.LibraryCommand;
import com.oocourse.library2.LibraryOpenCmd;
import com.oocourse.library2.LibraryReqCmd;
import com.oocourse.library2.LibraryCloseCmd;
import com.oocourse.library2.LibraryBookId;

import java.time.LocalDate;
import java.util.Map;

import static com.oocourse.library2.LibraryIO.SCANNER;
import static com.oocourse.library2.LibraryReqCmd.Type.QUERIED;
import static com.oocourse.library2.LibraryReqCmd.Type.RETURNED;
import static com.oocourse.library2.LibraryReqCmd.Type.RESTORED;

public class MainClass {
    public static void main(String[] args) {
        Map<LibraryBookIsbn, Integer> bookList = SCANNER.getInventory();
        Library library = new Library(bookList); // 创建图书馆对象
        while (true) {
            LibraryCommand command = SCANNER.nextCommand();
            if (command == null) { break; }
            LocalDate today = command.getDate(); // 今天的日期
            if (command instanceof LibraryOpenCmd) {
                library.open(today);
            } else if (command instanceof LibraryCloseCmd) {
                library.close(today);
            } else {
                LibraryReqCmd req = (LibraryReqCmd) command;
                LibraryReqCmd.Type type = req.getType(); // 指令对应的类型（查询/阅读/借阅/预约/还书/取书/归还）
                LibraryBookIsbn bookIsbn = req.getBookIsbn(); // 指令对应的书籍ISBN号（type-uid）
                LibraryBookId bookId = null; // 指令对应书籍编号（type-uid-copyId）
                if (type == QUERIED || type == RETURNED || type == RESTORED) {
                    bookId = req.getBookId(); // 指令对应书籍编号（type-uid-copyId）
                }
                String studentId = req.getStudentId(); // 指令对应的用户Id
                switch (type) {
                    case QUERIED: {
                        library.userQueryBook(bookId, today);
                        break;
                    }
                    case BORROWED: {
                        library.userBorrowBook(bookIsbn, studentId, req);
                        break;
                    }
                    case ORDERED: {
                        library.userOrderBook(bookIsbn, studentId, req);
                        break;
                    }
                    case RETURNED: {
                        library.userReturnBook(bookId, studentId, req);
                        break;
                    }
                    case PICKED: {
                        library.userPickBook(bookIsbn, studentId, req);
                        break;
                    }
                    case READ: {
                        library.userReadBook(bookIsbn, studentId, req);
                        break;
                    }
                    case RESTORED: {
                        library.userRestoreBook(bookId, studentId, req);
                        break;
                    }
                    default: {
                    }
                }
            }
        }
    }
}
