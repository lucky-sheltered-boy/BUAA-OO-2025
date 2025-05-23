import com.oocourse.spec1.exceptions.AcquaintanceNotFoundException;
import com.oocourse.spec1.exceptions.EqualRelationException;
import com.oocourse.spec1.exceptions.EqualTagIdException;
import com.oocourse.spec1.exceptions.RelationNotFoundException;
import com.oocourse.spec1.exceptions.TagIdNotFoundException;
import com.oocourse.spec1.exceptions.EqualPersonIdException;
import com.oocourse.spec1.exceptions.PersonIdNotFoundException;
import com.oocourse.spec1.main.NetworkInterface;
import com.oocourse.spec1.main.PersonInterface;
import com.oocourse.spec1.main.TagInterface;

import java.util.HashMap;

public class Network implements NetworkInterface {
    private HashMap<Integer, PersonInterface> persons = new HashMap<>();
    private int tripleSum = 0;
    
    public Network() {
    }
    
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
            } else {
                person1.modifyRelation(person2, value, false);
                person2.modifyRelation(person1, value, false);
                tripleSum -= getNumOfSameLinkedPersons(id1, id2);
            }
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
    
    public PersonInterface[] getPersons() {
        return null;
    }
   
    public HashMap<Integer, PersonInterface> getPersonsMap() {
        return persons;
    }
}
