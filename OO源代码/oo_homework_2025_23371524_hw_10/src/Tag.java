import com.oocourse.spec2.main.PersonInterface;
import com.oocourse.spec2.main.TagInterface;

import java.util.HashMap;

public class Tag implements TagInterface {
    private int id;
    private int sum = 0;
    private int count = 0;
    private HashMap<Integer, PersonInterface> persons = new HashMap<>();
    private int valueSum = 0;
    
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
            if (persons.size() < ((Person) person).getAcquaintance().size()) {
                for (PersonInterface temp : persons.values()) {
                    if (person.isLinked(temp)) {
                        valueSum += 2 * person.queryValue(temp);
                    }
                }
            } else {
                for (PersonInterface acquaintance : ((Person) person).getAcquaintance().values()) {
                    if (persons.containsKey(acquaintance.getId())) {
                        valueSum += 2 * person.queryValue(acquaintance);
                    }
                }
            }
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
    public int getValueSum() {
        return valueSum;
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
            if (persons.size() < ((Person) person).getAcquaintance().size()) {
                for (PersonInterface temp : persons.values()) {
                    if (person.isLinked(temp)) {
                        valueSum -= 2 * person.queryValue(temp);
                    }
                }
            } else {
                for (PersonInterface acquaintance : ((Person) person).getAcquaintance().values()) {
                    if (persons.containsKey(acquaintance.getId())) {
                        valueSum -= 2 * person.queryValue(acquaintance);
                    }
                }
            }
        }
    }
    
    @Override
    public int getSize() {
        return persons.size();
    }
    
    public void addValueSum(int value) {
        valueSum += value;
    }
    
    public HashMap<Integer, PersonInterface> getPersons() {
        return persons;
    }
}
