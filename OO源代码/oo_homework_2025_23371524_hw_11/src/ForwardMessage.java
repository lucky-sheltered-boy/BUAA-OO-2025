import com.oocourse.spec3.main.ForwardMessageInterface;
import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.PersonInterface;
import com.oocourse.spec3.main.TagInterface;

import static java.lang.Math.abs;

public class ForwardMessage implements ForwardMessageInterface {
    private int type;
    private TagInterface tag;
    private int id;
    private PersonInterface person1;
    private PersonInterface person2;
    private int articleId;
    
    public ForwardMessage(int messageId, int article,
        PersonInterface messagePerson1, PersonInterface messagePerson2) {
        type = 0;
        tag = null;
        id = messageId;
        person1 = messagePerson1;
        person2 = messagePerson2;
        articleId = article;
    }
    
    public ForwardMessage(int messageId, int article,
        PersonInterface messagePerson1, TagInterface messageTag) {
        type = 1;
        tag = messageTag;
        id = messageId;
        person1 = messagePerson1;
        person2 = null;
        articleId = article;
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
    public PersonInterface getPerson1() {
        return person1;
    }
    
    @Override
    public PersonInterface getPerson2() {
        return person2;
    }
    
    @Override
    public int getArticleId() {
        return articleId;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (obj != null && obj instanceof MessageInterface) {
            return ((MessageInterface) obj).getId() == id;
        } else {
            return false;
        }
    }
    
    @Override
    public int getSocialValue() {
        return abs(articleId) % 200;
    }
}