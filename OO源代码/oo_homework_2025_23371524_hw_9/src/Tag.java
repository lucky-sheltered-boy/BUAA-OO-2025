import com.oocourse.spec1.main.PersonInterface;
import com.oocourse.spec1.main.TagInterface;

import java.util.HashMap;

public class Tag implements TagInterface {
    private int id;
    private int sum = 0;
    private int count = 0;
    private HashMap<Integer, PersonInterface> persons = new HashMap<>();
    
    public Tag(int id) {
        this.id = id;
    }
    
    @Override
    public int getId() {
        return id;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (obj == null || !(obj instanceof TagInterface)) {
            return false;
        }
        return ((TagInterface) obj).getId() == id;
    }
    
    @Override
    public void addPerson(PersonInterface person) {
        if (person == null) {
            return;
        }
        if (!hasPerson(person)) {
            persons.put(person.getId(), person);
            sum += person.getAge();
            count++;
        }
    }
    
    @Override
    public boolean hasPerson(PersonInterface person) {
        if (person == null) {
            return false;
        }
        return persons.containsKey(person.getId());
    }
    
    @Override
    public int getAgeMean() {
        if (count == 0) {
            return 0;
        }
        return sum / count;
    }
    
    @Override
    public int getAgeVar() {
        int sum = 0;
        int count = 0;
        int mean = getAgeMean();
        for (PersonInterface person : persons.values()) {
            sum += (person.getAge() - mean) * (person.getAge() - mean);
            count++;
        }
        if (count == 0) {
            return 0;
        }
        return sum / count;
    }
    
    @Override
    public void delPerson(PersonInterface person) {
        if (person == null) {
            return;
        }
        if (hasPerson(person)) {
            persons.remove(person.getId());
            sum -= person.getAge();
            count--;
        }
    }
    
    @Override
    public int getSize() {
        return persons.size();
    }
}
