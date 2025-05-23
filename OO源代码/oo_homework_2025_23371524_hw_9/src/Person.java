import com.oocourse.spec1.main.PersonInterface;
import com.oocourse.spec1.main.TagInterface;

import java.util.HashMap;

public class Person implements PersonInterface {
    private int id;
    private String name;
    private int age;
    private HashMap<Integer, PersonInterface> acquaintance = new HashMap<>();
    //id <-> PersonInterface
    private HashMap<Integer, Integer> value = new HashMap<>();  //id <-> value
    private HashMap<Integer, TagInterface> tags = new HashMap<>();   //id <-> TagInterface
    
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
        }
    }
    
    public void modifyRelation(PersonInterface person, int value, boolean setFlag) {
        if (person == null) {
            return;
        }
        if (setFlag) {
            this.value.put(person.getId(), queryValue(person) + value);
        } else {
            this.acquaintance.remove(person.getId());
            this.value.remove(person.getId());
            for (TagInterface tag : tags.values()) {
                if (tag.hasPerson(person)) {
                    tag.delPerson(person);
                }
            }
        }
    }
    
    public boolean isCircle(PersonInterface person, HashMap<PersonInterface, Integer> visited) {
        if (person == null) {
            return false;
        }
        visited.put(this, 1);
        if (person.getId() == id) {
            return true;
        }
        for (PersonInterface acquaint : acquaintance.values()) {
            if (visited.containsKey(acquaint)) {
                continue;
            }
            if (acquaint.isLinked(person)) {
                return true;
            }
            if (((Person) acquaint).isCircle(person, visited)) {
                return true;
            }
        }
        return false;
    }
    
    public int getAcquaintanceSize() {
        return acquaintance.size();
    }
    
    public int getBestAcquaintance() {
        int value = Integer.MIN_VALUE;
        int bestId = -1;
        for (int id : this.value.keySet()) {
            if (this.value.get(id) > value) {
                value = this.value.get(id);
                bestId = id;
            } else if (this.value.get(id) == value && id < bestId) {
                bestId = id;
            }
        }
        return bestId;
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
    
    public HashMap<Integer, PersonInterface> getAcquaintance() {
        return acquaintance;
    }
    
    public boolean strictEquals(PersonInterface person) {
        return true;
    }
}
