import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.PersonInterface;
import com.oocourse.spec3.main.RedEnvelopeMessageInterface;
import com.oocourse.spec3.main.TagInterface;

public class RedEnvelopeMessage implements RedEnvelopeMessageInterface {
    private int type;
    private TagInterface tag;
    private int id;
    private PersonInterface person1;
    private PersonInterface person2;
    private int money;
    
    public RedEnvelopeMessage(int messageId, int luckyMoney,
        PersonInterface messagePerson1, PersonInterface messagePerson2) {
        type = 0;
        tag = null;
        id = messageId;
        person1 = messagePerson1;
        person2 = messagePerson2;
        money = luckyMoney;
    }
    
    public RedEnvelopeMessage(int messageId, int luckyMoney,
        PersonInterface messagePerson1, TagInterface messageTag) {
        type = 1;
        tag = messageTag;
        id = messageId;
        person1 = messagePerson1;
        person2 = null;
        money = luckyMoney;
    }
    
    @Override
    public int getType() {
        return type;
    }
    
    @Override
    public TagInterface getTag() {
        return tag;
    }
    
    @Override
    public int getId() {
        return id;
    }
    
    @Override
    public int getSocialValue() {
        return money * 5;
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
    public int getMoney() {
        return money;
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
