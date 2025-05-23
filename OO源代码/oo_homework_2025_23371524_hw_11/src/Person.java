import com.oocourse.spec3.main.MessageInterface;
import com.oocourse.spec3.main.PersonInterface;
import com.oocourse.spec3.main.TagInterface;

import java.util.HashMap;
import java.util.HashSet;
import java.util.ArrayDeque;
import java.util.ArrayList;

public class Person implements PersonInterface {
    private int id;
    private String name;
    private int age;
    private HashMap<Integer, PersonInterface> acquaintance = new HashMap<>();
    // personId <-> PersonInterface
    private HashMap<Integer, Integer> value = new HashMap<>();
    // personId <-> value
    private HashMap<Integer, TagInterface> tags = new HashMap<>();
    // tagId <-> TagInterface
    private ArticleNode articleHead = new ArticleNode(0);
    private HashMap<Integer, ArrayList<ArticleNode>> articleNodes = new HashMap<>();
    // articleId <-> ArticleNode
    private int bestAcquaintanceId = -1;
    private int bestAcquaintanceValue = Integer.MIN_VALUE;
    private int socialValue = 0;
    private int money = 0;
    private ArrayList<MessageInterface> messages = new ArrayList<>();
    private int numOfArticleNode = 0;
    
    public Person(int id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
    
    @Override
    public int getId() {
        return id;
    }
    
    @Override
    public String getName() {
        return name;
    }
    
    @Override
    public int getAge() {
        return age;
    }
    
    @Override
    public boolean containsTag(int id) {
        return tags.containsKey(id);
    }
    
    @Override
    public TagInterface getTag(int id) {
        if (!containsTag(id)) {
            return null;
        }
        return tags.get(id);
    }
    
    @Override
    public void addTag(TagInterface tag) {
        if (tag == null) {
            return;
        }
        if (!containsTag(tag.getId())) {
            tags.put(tag.getId(), tag);
        }
    }
    
    @Override
    public void delTag(int id) {
        if (containsTag(id)) {
            tags.remove(id);
        }
    }
    
    @Override
    public boolean equals(Object obj) {
        if (obj == null || !(obj instanceof PersonInterface)) {
            return false;
        }
        return ((PersonInterface) obj).getId() == id;
    }
    
    @Override
    public boolean isLinked(PersonInterface person) {
        if (person == null) {
            return false;
        }
        if (person.getId() == id) {
            return true;
        }
        return this.acquaintance.containsKey(person.getId());
    }
    
    @Override
    public int queryValue(PersonInterface person) {
        if (person == null) {
            return 0;
        }
        if (acquaintance.containsKey(person.getId())) {
            return value.get(person.getId());
        } else {
            return 0;
        }
    }
    
    public void addRelation(PersonInterface person, int value) {
        if (person == null) {
            return;
        }
        if (!isLinked(person)) {
            acquaintance.put(person.getId(), person);
            this.value.put(person.getId(), value);
            if (value > bestAcquaintanceValue ||
                (value == bestAcquaintanceValue && person.getId() < bestAcquaintanceId)) {
                bestAcquaintanceValue = value;
                bestAcquaintanceId = person.getId();
            }
        }
    }
    
    public void modifyRelation(PersonInterface person, int value, boolean setFlag) {
        if (person == null) {
            return;
        }
        if (setFlag) {
            this.value.put(person.getId(), queryValue(person) + value);
            int afterValue = this.value.get(person.getId());
            if (person.getId() == bestAcquaintanceId) {
                if (afterValue >= bestAcquaintanceValue) {
                    bestAcquaintanceValue = afterValue;
                } else {
                    bestAcquaintanceValue = Integer.MIN_VALUE;
                    bestAcquaintanceId = -1;
                    for (int id : this.value.keySet()) {
                        if (this.value.get(id) > bestAcquaintanceValue ||
                            (this.value.get(id) == bestAcquaintanceValue &&
                            id < bestAcquaintanceId)) {
                            bestAcquaintanceValue = this.value.get(id);
                            bestAcquaintanceId = id;
                        }
                    }
                }
            } else {
                if (afterValue > bestAcquaintanceValue ||
                    (afterValue == bestAcquaintanceValue && person.getId() < bestAcquaintanceId)) {
                    bestAcquaintanceValue = afterValue;
                    bestAcquaintanceId = person.getId();
                }
            }
        } else {
            this.acquaintance.remove(person.getId());
            this.value.remove(person.getId());
            for (TagInterface tag : tags.values()) {
                if (tag.hasPerson(person)) {
                    tag.delPerson(person);
                }
            }
            if (person.getId() == bestAcquaintanceId) {
                bestAcquaintanceValue = Integer.MIN_VALUE;
                bestAcquaintanceId = -1;
                for (int id : this.value.keySet()) {
                    if (this.value.get(id) > bestAcquaintanceValue ||
                        (this.value.get(id) == bestAcquaintanceValue && id < bestAcquaintanceId)) {
                        bestAcquaintanceValue = this.value.get(id);
                        bestAcquaintanceId = id;
                    }
                }
            }
        }
    }
    
    public boolean isCircle(PersonInterface person, HashMap<PersonInterface, Integer> visited) {
        if (person == null) {
            return false;
        }
        visited.put(this, 1);
        if (this.isLinked(person)) {
            return true;
        }
        for (PersonInterface acquaint : acquaintance.values()) {
            if (visited.containsKey(acquaint)) {
                continue;
            }
            if (((Person) acquaint).isCircle(person, visited)) {
                return true;
            }
        }
        return false;
    }
    
    public HashMap<Integer, PersonInterface> getAcquaintance() {
        return acquaintance;
    }
    
    public int getAcquaintanceSize() {
        return acquaintance.size();
    }
    
    public int getBestAcquaintance() {
        return bestAcquaintanceId;
    }
    
    public int getNumOfSameLinkedPersons(PersonInterface person) {
        if (person == null) {
            return 0;
        }
        int num = 0;
        for (PersonInterface acquaintance : acquaintance.values()) {
            if (acquaintance.isLinked(person) && !acquaintance.equals(person)
                && !acquaintance.equals(this)) {
                num++;
            }
        }
        return num;
    }
    
    public boolean strictEquals(PersonInterface person) {
        return true;
    }
    
    public int getShortestPath(PersonInterface person) {
        HashSet<PersonInterface> visited = new HashSet<>();
        ArrayDeque<PersonInterface> queue = new ArrayDeque<>();
        queue.offer(this);
        visited.add(this);
        int distance = 0;
        while (!queue.isEmpty()) {
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                Person current = (Person) queue.poll();
                if (current != null && current.getId() == person.getId()) {
                    return distance;
                }
                if (current != null) {
                    for (PersonInterface acquaintance : current.getAcquaintance().values()) {
                        if (!visited.contains(acquaintance)) {
                            if (acquaintance.getId() == person.getId()) {
                                return distance + 1;
                            }
                            visited.add(acquaintance);
                            queue.offer(acquaintance);
                        }
                    }
                }
            }
            distance++;
        }
        return -1;
    }
    
    @Override
    public ArrayList<Integer> getReceivedArticles() {
        int size = numOfArticleNode;
        ArrayList<Integer> result = new ArrayList<>();
        ArticleNode current = articleHead.getNext();
        for (int i = 0; i < size; i++) {
            result.add(current.getArticleId());
            current = current.getNext();
        }
        return result;
    }
    
    @Override
    public ArrayList<Integer> queryReceivedArticles() {
        int size = Math.min(numOfArticleNode, 5);
        ArrayList<Integer> result = new ArrayList<>();
        ArticleNode current = articleHead.getNext();
        for (int i = 0; i < size; i++) {
            result.add(current.getArticleId());
            current = current.getNext();
        }
        return result;
    }
    
    public void addArticleToFirst(int articleId) {
        ArticleNode node = new ArticleNode(articleId);
        ArticleNode originalFirst = articleHead.getNext();
        articleHead.setNext(node);
        node.setPrev(articleHead);
        node.setNext(originalFirst);
        if (originalFirst != null) {
            originalFirst.setPrev(node);
        }
        if (!articleNodes.containsKey(articleId)) {
            articleNodes.put(articleId, new ArrayList<>());
        }
        articleNodes.get(articleId).add(node);
        numOfArticleNode++;
    }
    
    public void delArticle(int articleId) {
        if (!articleNodes.containsKey(articleId)) {
            return;
        }
        for (ArticleNode node : articleNodes.get(articleId)) {
            if (node != null) {
                ArticleNode prev = node.getPrev();
                ArticleNode next = node.getNext();
                if (prev != null) {
                    prev.setNext(next);
                }
                if (next != null) {
                    next.setPrev(prev);
                }
                numOfArticleNode--;
            }
        }
        articleNodes.remove(articleId);
    }
    
    public HashMap<Integer, TagInterface> getTags() {
        return tags;
    }
    
    @Override
    public void addSocialValue(int num) {
        socialValue += num;
    }
    
    @Override
    public int getSocialValue() {
        return socialValue;
    }
    
    @Override
    public void addMoney(int num) {
        money += num;
    }
    
    @Override
    public int getMoney() {
        return money;
    }
    
    @Override
    public ArrayList<MessageInterface> getMessages() {
        return messages;
    }
    
    @Override
    public ArrayList<MessageInterface> getReceivedMessages() {
        int size = Math.min(messages.size(), 5);
        ArrayList<MessageInterface> result = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            result.add(messages.get(i));
        }
        return result;
    }
    
    public void addMessageToFirst(MessageInterface message) {
        if (message == null) {
            return;
        }
        messages.add(0, message);
    }
}
