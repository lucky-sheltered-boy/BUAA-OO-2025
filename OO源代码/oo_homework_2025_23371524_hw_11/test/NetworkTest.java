import com.oocourse.spec3.main.EmojiMessageInterface;
import com.oocourse.spec3.main.ForwardMessageInterface;
import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.RedEnvelopeMessageInterface;
import org.junit.Before;
import org.junit.Test;
import com.oocourse.spec3.exceptions.*;

import java.util.HashMap;

import static org.junit.Assert.*;

public class NetworkTest {
    private static int personId = 0;
    private static int emojiId = 0;
    private static int messageId = 0;
    private MessageInterface[] beforeMessages;
    private MessageInterface[] afterMessages;
    private int[] beforeEmojiIdList;
    private int[] afterEmojiIdList;
    private int[] beforeEmojiHeatList;
    private int[] afterEmojiHeatList;
    
    @Test
    public void deleteColdEmoji() throws Exception {
        Network network = new Network();
        Person person1 = new Person(++personId, "A", 1);
        network.addPerson(person1);
        Person person2 = new Person(++personId, "B", 2);
        network.addPerson(person2);
        Person person3 = new Person(++personId, "C", 3);
        network.addPerson(person3);
        Person person4 = new Person(++personId, "D", 4);
        network.addPerson(person4);
        Person person5 = new Person(++personId, "E", 5);
        network.addPerson(person5);
        
        network.addRelation(person1.getId(), person2.getId(), 1);
        network.addRelation(person1.getId(), person3.getId(), 2);
        network.addRelation(person1.getId(), person4.getId(), 3);
        network.addRelation(person1.getId(), person5.getId(), 4);
        network.addRelation(person2.getId(), person3.getId(), 5);
        network.addRelation(person2.getId(), person4.getId(), 6);
        network.addRelation(person2.getId(), person5.getId(), 7);
        network.addRelation(person3.getId(), person4.getId(), 8);
        network.addRelation(person3.getId(), person5.getId(), 9);
        network.addRelation(person4.getId(), person5.getId(), 10);
        
        
        network.storeEmojiId(++emojiId);
        network.storeEmojiId(++emojiId);
        network.storeEmojiId(++emojiId);
        network.storeEmojiId(++emojiId);
        network.storeEmojiId(++emojiId);
        
        addHeat(network, 1, person1, person2);
        
        addHeat(network, 2, person1, person3);
        addHeat(network, 2, person1, person3);
        
        addHeat(network, 3, person1, person4);
        addHeat(network, 3, person1, person4);
        addHeat(network, 3, person1, person4);
        
        addHeat(network, 4, person1, person5);
        addHeat(network, 4, person1, person5);
        addHeat(network, 4, person1, person5);
        addHeat(network, 4, person1, person5);
        
        addHeat(network, 5, person2, person3);
        addHeat(network, 5, person2, person3);
        addHeat(network, 5, person2, person3);
        addHeat(network, 5, person2, person3);
        addHeat(network, 5, person2, person3);
        
        beforeMessages = network.getMessages();
        beforeEmojiIdList = network.getEmojiIdList();
        beforeEmojiHeatList = network.getEmojiHeatList();
        assertEquals(0, beforeMessages.length);
        assertEquals(5, beforeEmojiIdList.length);
        assertEquals(5, beforeEmojiHeatList.length);
        network.deleteColdEmoji(1);
        afterMessages = network.getMessages();
        afterEmojiIdList = network.getEmojiIdList();
        afterEmojiHeatList = network.getEmojiHeatList();
        assertEquals(0, afterMessages.length);
        assertEquals(5, afterEmojiIdList.length);
        assertEquals(5, afterEmojiHeatList.length);
        for (int i = 0; i < beforeEmojiIdList.length; i++) {
            assertEquals(beforeEmojiIdList[i], afterEmojiIdList[i]);
            assertEquals(beforeEmojiHeatList[i], afterEmojiHeatList[i]);
        }
        
        Tag tag1 = new Tag(1);
        network.addTag(person1.getId(), tag1);
        Message message1 = new Message(++messageId, 1, person1, person2);
        network.addMessage(message1);
        Message message2 = new Message(++messageId, 2, person1, tag1);
        network.addMessage(message2);
        RedEnvelopeMessage redEnvelopeMessage1 = new RedEnvelopeMessage(++messageId, 10, person1, person2);
        network.addMessage(redEnvelopeMessage1);
        RedEnvelopeMessage redEnvelopeMessage2 = new RedEnvelopeMessage(++messageId, 20, person1, tag1);
        network.addMessage(redEnvelopeMessage2);
        network.createOfficialAccount(person1.getId(), 1, "Official");
        network.contributeArticle(person1.getId(), 1, 1);
        ForwardMessage forwardMessage1 = new ForwardMessage(++messageId, 1, person1, person2);
        network.addMessage(forwardMessage1);
        ForwardMessage forwardMessage2 = new ForwardMessage(++messageId, 1, person1, tag1);
        network.addMessage(forwardMessage2);
        
        beforeMessages = network.getMessages();
        beforeEmojiIdList = network.getEmojiIdList();
        beforeEmojiHeatList = network.getEmojiHeatList();
        assertEquals(6, beforeMessages.length);
        assertEquals(5, beforeEmojiIdList.length);
        assertEquals(5, beforeEmojiHeatList.length);
        network.deleteColdEmoji(1);
        afterMessages = network.getMessages();
        afterEmojiIdList = network.getEmojiIdList();
        afterEmojiHeatList = network.getEmojiHeatList();
        assertEquals(6, afterMessages.length);
        assertEquals(5, afterEmojiIdList.length);
        assertEquals(5, afterEmojiHeatList.length);
        for (int i = 0; i < beforeMessages.length; i++) {
            assertTrue(strictEquals(beforeMessages[i], afterMessages[i]));
        }
        for (int i = 0; i < beforeEmojiIdList.length; i++) {
            assertEquals(beforeEmojiIdList[i], afterEmojiIdList[i]);
            assertEquals(beforeEmojiHeatList[i], afterEmojiHeatList[i]);
        }
        
        EmojiMessage emojiMessage1 = new EmojiMessage(++messageId, 1, person1, person2);
        network.addMessage(emojiMessage1);
        EmojiMessage emojiMessage2 = new EmojiMessage(++messageId, 1, person1, tag1);
        network.addMessage(emojiMessage2);
        EmojiMessage emojiMessage3 = new EmojiMessage(++messageId, 2, person1, person2);
        network.addMessage(emojiMessage3);
        EmojiMessage emojiMessage4 = new EmojiMessage(++messageId, 2, person1, tag1);
        network.addMessage(emojiMessage4);
        EmojiMessage emojiMessage5 = new EmojiMessage(++messageId, 3, person1, person2);
        network.addMessage(emojiMessage5);
        EmojiMessage emojiMessage6 = new EmojiMessage(++messageId, 3, person1, tag1);
        network.addMessage(emojiMessage6);
        EmojiMessage emojiMessage7 = new EmojiMessage(++messageId, 4, person1, person2);
        network.addMessage(emojiMessage7);
        EmojiMessage emojiMessage8 = new EmojiMessage(++messageId, 4, person1, tag1);
        network.addMessage(emojiMessage8);
        EmojiMessage emojiMessage9 = new EmojiMessage(++messageId, 5, person1, person2);
        network.addMessage(emojiMessage9);
        EmojiMessage emojiMessage10 = new EmojiMessage(++messageId, 5, person1, tag1);
        network.addMessage(emojiMessage10);
        
        beforeMessages = network.getMessages();
        beforeEmojiIdList = network.getEmojiIdList();
        beforeEmojiHeatList = network.getEmojiHeatList();
        HashMap<Integer, MessageInterface> messageMap = new HashMap<>();
        for (MessageInterface message : beforeMessages) {
            messageMap.put(message.getId(), message);
        }
        assertEquals(16, beforeMessages.length);
        assertEquals(5, beforeEmojiIdList.length);
        assertEquals(5, beforeEmojiHeatList.length);
        network.deleteColdEmoji(3);
        afterMessages = network.getMessages();
        afterEmojiIdList = network.getEmojiIdList();
        afterEmojiHeatList = network.getEmojiHeatList();
        assertEquals(12, afterMessages.length);
        assertEquals(3, afterEmojiIdList.length);
        assertEquals(3, afterEmojiHeatList.length);
        for (MessageInterface afterMessage : afterMessages) {
            assertTrue(messageMap.containsKey(afterMessage.getId()));
            assertTrue(strictEquals(messageMap.get(afterMessage.getId()), afterMessage));
        }
        for (int j : afterEmojiIdList) {
            assertTrue(j != 1 && j != 2);
        }
        for (int j : afterEmojiHeatList) {
            assertTrue(j != 1 && j != 2);
        }
        for (int i = 0; i < afterEmojiIdList.length; i++) {
            assertEquals(afterEmojiIdList[i], afterEmojiHeatList[i]);
        }
        for (MessageInterface afterMessage : afterMessages) {
            if (afterMessage instanceof EmojiMessageInterface) {
                assertTrue(((EmojiMessageInterface) afterMessage).getEmojiId() != 1 &&
                        ((EmojiMessageInterface) afterMessage).getEmojiId() != 2);
            }
        }
    }
    
    public void addHeat(Network network, int emojiId, Person person1, Person person2) throws Exception {
        EmojiMessage emojiMessage = new EmojiMessage(++messageId, emojiId, person1, person2);
        network.addMessage(emojiMessage);
        network.sendMessage(emojiMessage.getId());
    }
    
    public boolean strictEquals(MessageInterface message1, MessageInterface message2) {
        if (message1 instanceof EmojiMessageInterface && message2 instanceof EmojiMessageInterface) {
            return message1.getId() == message2.getId() &&
                    message1.getType() == message2.getType() &&
                    message1.getSocialValue() == message2.getSocialValue() &&
                    message1.getPerson1().equals(message2.getPerson1()) &&
                    (message1.getPerson2() == null && message2.getPerson2() == null || message1.getPerson2().equals(message2.getPerson2())) &&
                    (message1.getTag() == null && message2.getTag() == null || message1.getTag().equals(message2.getTag()));
        } else if (message1 instanceof RedEnvelopeMessageInterface && message2 instanceof RedEnvelopeMessageInterface) {
            return message1.getId() == message2.getId() &&
                    message1.getType() == message2.getType() &&
                    message1.getSocialValue() == message2.getSocialValue() &&
                    message1.getPerson1().equals(message2.getPerson1()) &&
                    (message1.getPerson2() == null && message2.getPerson2() == null || message1.getPerson2().equals(message2.getPerson2())) &&
                    (message1.getTag() == null && message2.getTag() == null || message1.getTag().equals(message2.getTag()));
        } else if (message1 instanceof ForwardMessageInterface && message2 instanceof ForwardMessageInterface) {
            return message1.getId() == message2.getId() &&
                    message1.getType() == message2.getType() &&
                    message1.getSocialValue() == message2.getSocialValue() &&
                    message1.getPerson1().equals(message2.getPerson1()) &&
                    (message1.getPerson2() == null && message2.getPerson2() == null || message1.getPerson2().equals(message2.getPerson2())) &&
                    (message1.getTag() == null && message2.getTag() == null || message1.getTag().equals(message2.getTag()));
        } else if (message1 instanceof MessageInterface && message2 instanceof MessageInterface) {
            return message1.getId() == message2.getId() &&
                    message1.getType() == message2.getType() &&
                    message1.getSocialValue() == message2.getSocialValue() &&
                    message1.getPerson1().equals(message2.getPerson1()) &&
                    (message1.getPerson2() == null && message2.getPerson2() == null || message1.getPerson2().equals(message2.getPerson2())) &&
                    (message1.getTag() == null && message2.getTag() == null || message1.getTag().equals(message2.getTag()));
        } else {
            return false;
        }
    }
}