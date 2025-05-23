import com.oocourse.spec3.exceptions.AcquaintanceNotFoundException;
import com.oocourse.spec3.exceptions.EmojiIdNotFoundException;
import com.oocourse.spec3.exceptions.EqualEmojiIdException;
import com.oocourse.spec3.exceptions.EqualMessageIdException;
import com.oocourse.spec3.exceptions.EqualPersonIdException;
import com.oocourse.spec3.exceptions.EqualRelationException;
import com.oocourse.spec3.exceptions.EqualTagIdException;
import com.oocourse.spec3.exceptions.MessageIdNotFoundException;
import com.oocourse.spec3.exceptions.PathNotFoundException;
import com.oocourse.spec3.exceptions.PersonIdNotFoundException;
import com.oocourse.spec3.exceptions.RelationNotFoundException;
import com.oocourse.spec3.exceptions.TagIdNotFoundException;
import com.oocourse.spec3.exceptions.DeleteOfficialAccountPermissionDeniedException;
import com.oocourse.spec3.exceptions.DeleteArticlePermissionDeniedException;
import com.oocourse.spec3.exceptions.OfficialAccountIdNotFoundException;
import com.oocourse.spec3.exceptions.ArticleIdNotFoundException;
import com.oocourse.spec3.exceptions.EqualOfficialAccountIdException;
import com.oocourse.spec3.exceptions.EqualArticleIdException;
import com.oocourse.spec3.exceptions.ContributePermissionDeniedException;
import com.oocourse.spec3.main.NetworkInterface;
import com.oocourse.spec3.main.OfficialAccountInterface;
import com.oocourse.spec3.main.PersonInterface;
import com.oocourse.spec3.main.TagInterface;
import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.EmojiMessageInterface;
import com.oocourse.spec3.main.ForwardMessageInterface;
import com.oocourse.spec3.main.RedEnvelopeMessageInterface;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

public class Network implements NetworkInterface {
    private HashMap<Integer, PersonInterface> persons = new HashMap<>();
    private HashMap<Integer, OfficialAccountInterface> accounts = new HashMap<>();
    private HashMap<Integer, PersonInterface> articles = new HashMap<>();
    private int tripleSum = 0;
    private int coupleSum = 0;
    private boolean dirtySignForCoupleSum = false;
    private HashMap<Integer, MessageInterface> messages = new HashMap<>();
    // messageId <-> MessageInterface
    private HashMap<Integer, Integer> emojiId2Heat = new HashMap<>();
    private HashMap<Integer, ArrayList<Integer>> emojiId2MessageId = new HashMap<>();
    private HashSet<TagInterface> tagList = new HashSet<>();
    
    public Network() { }
    
    @Override
    public boolean containsPerson(int id) {
        return persons.containsKey(id);
    }
    
    @Override
    public PersonInterface getPerson(int id) {
        if (!containsPerson(id)) {
            return null;
        }
        return persons.get(id);
    }
    
    @Override
    public void addPerson(PersonInterface person) throws EqualPersonIdException {
        if (person == null) {
            return;
        }
        if (containsPerson(person.getId())) {
            throw new EqualPersonIdException(person.getId());
        }
        persons.put(person.getId(), person);
    }
    
    @Override
    public void addRelation(int id1, int id2, int value) throws
        PersonIdNotFoundException, EqualRelationException {
        if (!containsPerson(id1) || !containsPerson(id2)
            || getPerson(id1).isLinked(getPerson(id2))) {
            if (!containsPerson(id1)) {
                throw new PersonIdNotFoundException(id1);
            } else if (!containsPerson(id2)) {
                throw new PersonIdNotFoundException(id2);
            } else {
                throw new EqualRelationException(id1, id2);
            }
        } else {
            Person person1 = (Person) getPerson(id1);
            Person person2 = (Person) getPerson(id2);
            person1.addRelation(person2, value);
            person2.addRelation(person1, value);
            tripleSum += getNumOfSameLinkedPersons(id1, id2);
            dirtySignForCoupleSum = true;
            for (TagInterface tag : tagList) {
                if (tag.hasPerson(person1) && tag.hasPerson(person2)) {
                    ((Tag) tag).addValueSum(2 * value);
                }
            }
        }
    }
    
    @Override
    public void modifyRelation(int id1, int id2, int value) throws
        PersonIdNotFoundException, EqualPersonIdException, RelationNotFoundException {
        if (!containsPerson(id1) || !containsPerson(id2) ||
            id1 == id2 || !getPerson(id1).isLinked(getPerson(id2))) {
            if (!containsPerson(id1)) {
                throw new PersonIdNotFoundException(id1);
            } else if (!containsPerson(id2)) {
                throw new PersonIdNotFoundException(id2);
            } else if (id1 == id2) {
                throw new EqualPersonIdException(id1);
            } else {
                throw new RelationNotFoundException(id1, id2);
            }
        } else {
            Person person1 = (Person) getPerson(id1);
            Person person2 = (Person) getPerson(id2);
            if (person1.queryValue(person2) + value > 0) {
                person1.modifyRelation(person2, value, true);
                person2.modifyRelation(person1, value, true);
                for (TagInterface tag : tagList) {
                    if (tag.hasPerson(person1) && tag.hasPerson(person2)) {
                        ((Tag) tag).addValueSum(2 * value);
                    }
                }
            } else {
                int originalValue = person1.queryValue(person2);
                for (TagInterface tag : tagList) {
                    if (tag.hasPerson(person1) && tag.hasPerson(person2)) {
                        ((Tag) tag).addValueSum(-2 * originalValue);
                    }
                }
                person1.modifyRelation(person2, value, false);
                person2.modifyRelation(person1, value, false);
                tripleSum -= getNumOfSameLinkedPersons(id1, id2);
            }
            dirtySignForCoupleSum = true;
        }
    }
    
    @Override
    public int queryValue(int id1, int id2) throws
        PersonIdNotFoundException, RelationNotFoundException {
        if (!containsPerson(id1) || !containsPerson(id2) ||
            !getPerson(id1).isLinked(getPerson(id2))) {
            if (!containsPerson(id1)) {
                throw new PersonIdNotFoundException(id1);
            } else if (!containsPerson(id2)) {
                throw new PersonIdNotFoundException(id2);
            } else {
                throw new RelationNotFoundException(id1, id2);
            }
        } else {
            return getPerson(id1).queryValue(getPerson(id2));
        }
    }
    
    @Override
    public boolean isCircle(int id1, int id2) throws PersonIdNotFoundException {
        if (!containsPerson(id1) || !containsPerson(id2)) {
            if (!containsPerson(id1)) {
                throw new PersonIdNotFoundException(id1);
            } else {
                throw new PersonIdNotFoundException(id2);
            }
        } else {
            Person person1 = (Person) getPerson(id1);
            Person person2 = (Person) getPerson(id2);
            HashMap<PersonInterface, Integer> visited = new HashMap<>();
            return person1.isCircle(person2, visited);
        }
    }
    
    @Override
    public int queryTripleSum() {
        return tripleSum;
    }
    
    @Override
    public void addTag(int personId, TagInterface tag) throws
        PersonIdNotFoundException, EqualTagIdException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (getPerson(personId).containsTag(tag.getId())) {
            throw new EqualTagIdException(tag.getId());
        } else {
            getPerson(personId).addTag(tag);
            tagList.add(tag);
        }
    }
    
    @Override
    public void addPersonToTag(int personId1, int personId2, int tagId)
        throws PersonIdNotFoundException, RelationNotFoundException,
        TagIdNotFoundException, EqualPersonIdException {
        if (!containsPerson(personId1)) {
            throw new PersonIdNotFoundException(personId1);
        } else if (!containsPerson(personId2)) {
            throw new PersonIdNotFoundException(personId2);
        } else if (personId1 == personId2) {
            throw new EqualPersonIdException(personId1);
        } else if (!getPerson(personId2).isLinked(getPerson(personId1))) {
            throw new RelationNotFoundException(personId1, personId2);
        } else if (!getPerson(personId2).containsTag(tagId)) {
            throw new TagIdNotFoundException(tagId);
        } else if (getPerson(personId2).getTag(tagId).hasPerson(getPerson(personId1))) {
            throw new EqualPersonIdException(personId1);
        } else {
            if (getPerson(personId2).getTag(tagId).getSize() <= 999) {
                getPerson(personId2).getTag(tagId).addPerson(getPerson(personId1));
            }
        }
    }
    
    @Override
    public int queryTagValueSum(int personId, int tagId) throws
        PersonIdNotFoundException, TagIdNotFoundException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!getPerson(personId).containsTag(tagId)) {
            throw new TagIdNotFoundException(tagId);
        } else {
            return getPerson(personId).getTag(tagId).getValueSum();
        }
    }
    
    @Override
    public int queryTagAgeVar(int personId, int tagId) throws
        PersonIdNotFoundException, TagIdNotFoundException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!getPerson(personId).containsTag(tagId)) {
            throw new TagIdNotFoundException(tagId);
        } else {
            return getPerson(personId).getTag(tagId).getAgeVar();
        }
    }
    
    @Override
    public void delPersonFromTag(int personId1, int personId2, int tagId)
        throws PersonIdNotFoundException, TagIdNotFoundException {
        if (!containsPerson(personId1)) {
            throw new PersonIdNotFoundException(personId1);
        } else if (!containsPerson(personId2)) {
            throw new PersonIdNotFoundException(personId2);
        } else if (!getPerson(personId2).containsTag(tagId)) {
            throw new TagIdNotFoundException(tagId);
        } else if (!getPerson(personId2).getTag(tagId).hasPerson(getPerson(personId1))) {
            throw new PersonIdNotFoundException(personId1);
        } else {
            getPerson(personId2).getTag(tagId).delPerson(getPerson(personId1));
        }
    }
    
    @Override
    public void delTag(int personId, int tagId) throws
        PersonIdNotFoundException, TagIdNotFoundException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!getPerson(personId).containsTag(tagId)) {
            throw new TagIdNotFoundException(tagId);
        } else {
            getPerson(personId).delTag(tagId);
            tagList.remove(getPerson(personId).getTag(tagId));
        }
    }
    
    @Override
    public int queryBestAcquaintance(int id) throws
        PersonIdNotFoundException, AcquaintanceNotFoundException {
        if (!containsPerson(id)) {
            throw new PersonIdNotFoundException(id);
        } else if (((Person) getPerson(id)).getAcquaintanceSize() == 0) {
            throw new AcquaintanceNotFoundException(id);
        } else {
            return ((Person) getPerson(id)).getBestAcquaintance();
        }
    }
    
    public int getNumOfSameLinkedPersons(int id1, int id2) {
        return ((Person) getPerson(id1)).getNumOfSameLinkedPersons(getPerson(id2));
    }
   
    @Override
    public int queryCoupleSum() {
        if (!dirtySignForCoupleSum) {
            return coupleSum;
        }
        int sum = 0;
        HashSet<PersonInterface> counted = new HashSet<>();
        for (PersonInterface person : persons.values()) {
            if (counted.contains(person)) {
                continue;
            }
            counted.add(person);
            if (((Person) person).getAcquaintanceSize() == 0) {
                continue;
            }
            int bestId = ((Person) person).getBestAcquaintance();
            if (!persons.containsKey(bestId)) {
                continue;
            }
            PersonInterface best = persons.get(bestId);
            if (counted.contains(best)) {
                continue;
            }
            if (((Person) best).getAcquaintanceSize() == 0) {
                continue;
            }
            int bestBestId = ((Person) best).getBestAcquaintance();
            if (bestBestId == person.getId()) {
                sum += 1;
                counted.add(best);
            }
        }
        coupleSum = sum;
        dirtySignForCoupleSum = false;
        return coupleSum;
    }
    
    @Override
    public int queryShortestPath(int id1,int id2) throws
        PersonIdNotFoundException, PathNotFoundException {
        HashMap<PersonInterface, Integer> visited = new HashMap<>();
        if (!containsPerson(id1)) {
            throw new PersonIdNotFoundException(id1);
        } else if (!containsPerson(id2)) {
            throw new PersonIdNotFoundException(id2);
        } else {
            if (id1 == id2) {
                return 0;
            }
            int ans = ((Person) persons.get(id1)).getShortestPath(persons.get(id2));
            if (ans == -1) {
                throw new PathNotFoundException(id1, id2);
            } else {
                return ans;
            }
        }
    }
    
    @Override
    public boolean containsAccount(int id) { return accounts.containsKey(id); }
    
    @Override
    public void createOfficialAccount(int personId, int accountId, String name) throws
        PersonIdNotFoundException, EqualOfficialAccountIdException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (containsAccount(accountId)) {
            throw new EqualOfficialAccountIdException(accountId);
        } else {
            accounts.put(accountId, new OfficialAccount(personId, accountId, name));
            accounts.get(accountId).addFollower(persons.get(personId));
        }
    }
    
    @Override
    public void deleteOfficialAccount(int personId, int accountId) throws
        OfficialAccountIdNotFoundException, PersonIdNotFoundException,
        DeleteOfficialAccountPermissionDeniedException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!containsAccount(accountId)) {
            throw new OfficialAccountIdNotFoundException(accountId);
        } else if (accounts.get(accountId).getOwnerId() != personId) {
            throw new DeleteOfficialAccountPermissionDeniedException(personId, accountId);
        } else {
            accounts.remove(accountId);
        }
    }
    
    @Override
    public boolean containsArticle(int id) { return articles.containsKey(id); }
    
    @Override
    public void contributeArticle(int personId,int accountId,int articleId) throws
        PersonIdNotFoundException, OfficialAccountIdNotFoundException,
        EqualArticleIdException, ContributePermissionDeniedException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!containsAccount(accountId)) {
            throw new OfficialAccountIdNotFoundException(accountId);
        } else if (containsArticle(articleId)) {
            throw new EqualArticleIdException(articleId);
        } else if (!accounts.get(accountId).containsFollower(persons.get(personId))) {
            throw new ContributePermissionDeniedException(personId, articleId);
        } else {
            articles.put(articleId, persons.get(personId));
            accounts.get(accountId).addArticle(persons.get(personId), articleId);
            ((OfficialAccount) accounts.get(accountId)).addArticleToAllFollowers(articleId);
        }
    }
    
    @Override
    public void deleteArticle(int personId,int accountId,int articleId) throws
        PersonIdNotFoundException, OfficialAccountIdNotFoundException,
        ArticleIdNotFoundException, DeleteArticlePermissionDeniedException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!containsAccount(accountId)) {
            throw new OfficialAccountIdNotFoundException(accountId);
        } else if (!accounts.get(accountId).containsArticle(articleId)) {
            throw new ArticleIdNotFoundException(articleId);
        } else if (accounts.get(accountId).getOwnerId() != personId) {
            throw new DeleteArticlePermissionDeniedException(personId, articleId);
        } else {
            ((OfficialAccount) accounts.get(accountId)).delArticle(articleId);
        }
    }
    
    @Override
    public void followOfficialAccount(int personId,int accountId) throws
        PersonIdNotFoundException, OfficialAccountIdNotFoundException, EqualPersonIdException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else if (!containsAccount(accountId)) {
            throw new OfficialAccountIdNotFoundException(accountId);
        } else if (accounts.get(accountId).containsFollower(persons.get(personId))) {
            throw new EqualPersonIdException(personId);
        } else {
            accounts.get(accountId).addFollower(persons.get(personId));
        }
    }
    
    @Override
    public int queryBestContributor(int id) throws OfficialAccountIdNotFoundException {
        if (!containsAccount(id)) {
            throw new OfficialAccountIdNotFoundException(id);
        } else {
            return accounts.get(id).getBestContributor();
        }
    }
    
    @Override
    public ArrayList<Integer> queryReceivedArticles(int personId) throws
        PersonIdNotFoundException {
        if (!containsPerson(personId)) {
            throw new PersonIdNotFoundException(personId);
        } else {
            return (ArrayList<Integer>) persons.get(personId).queryReceivedArticles();
        }
    }
    
    @Override
    public boolean containsMessage(int id) {
        return messages.containsKey(id);
    }
    
    public boolean containsEmojiId(int id) {
        return emojiId2Heat.containsKey(id);
    }
    
    @Override
    public void addMessage(MessageInterface message) throws
        EqualMessageIdException, EmojiIdNotFoundException,
        EqualPersonIdException, ArticleIdNotFoundException {
        if (containsMessage(message.getId())) {
            throw new EqualMessageIdException(message.getId());
        } else if ((message instanceof EmojiMessageInterface) &&
            !containsEmojiId(((EmojiMessageInterface) message).getEmojiId())) {
            throw new EmojiIdNotFoundException(((EmojiMessageInterface) message).getEmojiId());
        } else if ((message instanceof ForwardMessageInterface) &&
            !containsArticle(((ForwardMessageInterface) message).getArticleId())) {
            throw new ArticleIdNotFoundException(((ForwardMessageInterface) message).
            getArticleId());
        } else if ((message instanceof ForwardMessageInterface) &&
            containsArticle(((ForwardMessageInterface) message).getArticleId()) &&
            !(message.getPerson1().getReceivedArticles().
            contains(((ForwardMessageInterface) message).getArticleId()))) {
            throw new ArticleIdNotFoundException(((ForwardMessageInterface) message).
            getArticleId());
        } else if (message.getType() == 0 && message.getPerson1().equals(message.getPerson2())) {
            throw new EqualPersonIdException(message.getPerson1().getId());
        } else {
            messages.put(message.getId(), message);
            if (message instanceof EmojiMessageInterface) {
                if (!emojiId2MessageId.containsKey(((EmojiMessageInterface)message).getEmojiId())) {
                    emojiId2MessageId.put(((EmojiMessageInterface) message).getEmojiId(),
                        new ArrayList<>());
                }
                emojiId2MessageId.get(((EmojiMessageInterface) message).getEmojiId()).add(
                    message.getId());
            }
        }
    }
    
    @Override
    public MessageInterface getMessage(int id) {
        if (!containsMessage(id)) {
            return null;
        } else {
            return messages.get(id);
        }
    }
    
    @Override
    public int querySocialValue(int id) throws PersonIdNotFoundException {
        if (!containsPerson(id)) {
            throw new PersonIdNotFoundException(id);
        } else {
            return (persons.get(id)).getSocialValue();
        }
    }
    
    @Override
    public ArrayList<MessageInterface> queryReceivedMessages(int id) throws
        PersonIdNotFoundException {
        if (!containsPerson(id)) {
            throw new PersonIdNotFoundException(id);
        } else {
            return (ArrayList<MessageInterface>) getPerson(id).getReceivedMessages();
        }
    }
    
    @Override
    public void storeEmojiId(int id) throws EqualEmojiIdException {
        if (containsEmojiId(id)) {
            throw new EqualEmojiIdException(id);
        } else {
            emojiId2Heat.put(id, 0);
        }
    }
    
    @Override
    public int queryMoney(int id) throws PersonIdNotFoundException {
        if (!containsPerson(id)) {
            throw new PersonIdNotFoundException(id);
        } else {
            return (persons.get(id)).getMoney();
        }
    }
    
    @Override
    public int queryPopularity(int id) throws EmojiIdNotFoundException {
        if (!containsEmojiId(id)) {
            throw new EmojiIdNotFoundException(id);
        } else {
            return emojiId2Heat.get(id);
        }
    }
    
    @Override
    public int deleteColdEmoji(int limit) {
        ArrayList<Integer> toDelete = new ArrayList<>();
        for (int emojiId : emojiId2Heat.keySet()) {
            if (emojiId2Heat.get(emojiId) < limit) {
                toDelete.add(emojiId);
                if (emojiId2MessageId.containsKey(emojiId)) {
                    for (int messageId : emojiId2MessageId.get(emojiId)) {
                        messages.remove(messageId);
                    }
                    emojiId2MessageId.remove(emojiId);
                }
            }
        }
        for (int emojiId : toDelete) {
            emojiId2Heat.remove(emojiId);
        }
        return emojiId2Heat.size();
    }
    
    @Override
    public void sendMessage(int id) throws
        RelationNotFoundException, MessageIdNotFoundException, TagIdNotFoundException {
        if (!containsMessage(id)) {
            throw new MessageIdNotFoundException(id);
        } else if (getMessage(id).getType() == 0 &&
            !(getMessage(id).getPerson1().isLinked(getMessage(id).getPerson2()))) {
            throw new RelationNotFoundException(getMessage(id).getPerson1().getId(),
            getMessage(id).getPerson2().getId());
        } else if (getMessage(id).getType() == 1 &&
            !getMessage(id).getPerson1().containsTag(getMessage(id).getTag().getId())) {
            throw new TagIdNotFoundException(getMessage(id).getTag().getId());
        } else {
            MessageInterface message = getMessage(id);
            PersonInterface person1 = message.getPerson1();
            PersonInterface person2 = message.getPerson2();
            if (message.getType() == 0 && person1.isLinked(person2) && person1 != person2) {
                person1.addSocialValue(message.getSocialValue());
                person2.addSocialValue(message.getSocialValue());
                if (message instanceof RedEnvelopeMessageInterface) {
                    person1.addMoney(-((RedEnvelopeMessageInterface) message).getMoney());
                    person2.addMoney(((RedEnvelopeMessageInterface) message).getMoney());
                } else if (message instanceof ForwardMessageInterface) {
                    ((Person) person2).addArticleToFirst(((ForwardMessageInterface) message).
                        getArticleId());
                } else if (message instanceof EmojiMessageInterface) {
                    emojiId2Heat.put(((EmojiMessageInterface) message).getEmojiId(),
                        emojiId2Heat.get(((EmojiMessageInterface) message).getEmojiId()) + 1);
                }
                ((Person) person2).addMessageToFirst(message);
                messages.remove(id);
                if (message instanceof EmojiMessageInterface) {
                    emojiId2MessageId.get(((EmojiMessageInterface)message).getEmojiId()).
                        remove((Integer) id);
                }
            } else if (message.getType() == 1 && person1.containsTag(message.getTag().getId())) {
                TagInterface tag = message.getTag();
                person1.addSocialValue(message.getSocialValue());
                ((Tag) tag).addSocialValue(message.getSocialValue());
                int sizeOfPerson = tag.getSize();
                if (message instanceof RedEnvelopeMessageInterface && sizeOfPerson > 0) {
                    int moneyPerPerson = ((RedEnvelopeMessageInterface) message).getMoney() /
                        sizeOfPerson;
                    person1.addMoney(-moneyPerPerson * sizeOfPerson);
                    ((Tag) tag).addMoney(moneyPerPerson);
                } else if (message instanceof ForwardMessageInterface && sizeOfPerson > 0) {
                    ((Tag) tag).addArticleToAll(((ForwardMessageInterface) message).getArticleId());
                } else if (message instanceof EmojiMessageInterface) {
                    emojiId2Heat.put(((EmojiMessageInterface) message).getEmojiId(),
                        emojiId2Heat.get(((EmojiMessageInterface) message).getEmojiId()) + 1);
                }
                ((Tag) tag).addMessageToAll(message);
                messages.remove(id);
                if (message instanceof EmojiMessageInterface) {
                    emojiId2MessageId.get(((EmojiMessageInterface)message).getEmojiId()).
                        remove((Integer) id);
                }
            }
        }
    }
    
    public MessageInterface[] getMessages() { return null; }
    
    public int[] getEmojiIdList() { return null; }
    
    public int[] getEmojiHeatList() { return null; }
}