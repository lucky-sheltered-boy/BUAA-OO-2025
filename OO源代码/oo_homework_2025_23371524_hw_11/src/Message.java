import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.PersonInterface;
import com.oocourse.spec3.main.TagInterface;

public class Message implements MessageInterface {
    private int type;
    private TagInterface tag;
    private int id;
    private int socialValue;
    private PersonInterface person1;
    private PersonInterface person2;
    
    public Message(int messageId, int messageSocialValue, PersonInterface messagePerson1,
        PersonInterface messagePerson2) {
        type = 0;
        tag = null;
        id = messageId;
        socialValue = messageSocialValue;
        person1 = messagePerson1;
        person2 = messagePerson2;
    }
    
    public Message(int messageId, int messageSocialValue, PersonInterface messagePerson1,
        TagInterface messageTag) {
        type = 1;
        tag = messageTag;
        id = messageId;
        socialValue = messageSocialValue;
        person1 = messagePerson1;
        person2 = null;
    }
    
    @Override
    public int getType() {
        return type;
    }
    
    @Override
    public int getId() {
        return id;
    }
    
    @Override
    public int getSocialValue() {
        return socialValue;
    }
    
    @Override
    public PersonInterface getPerson1() {
        return person1;
    }
    
    @Override
    public PersonInterface getPerson2() {
        return person2;
    }
    
    @Override
    public TagInterface getTag() {
        return tag;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (obj != null && obj instanceof MessageInterface) {
            return ((MessageInterface) obj).getId() == id;
        } else {
            return false;
        }
    }
}