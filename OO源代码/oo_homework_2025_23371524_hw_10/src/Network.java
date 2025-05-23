import com.oocourse.spec2.exceptions.EqualOfficialAccountIdException;
import com.oocourse.spec2.exceptions.EqualPersonIdException;
import com.oocourse.spec2.exceptions.EqualRelationException;
import com.oocourse.spec2.exceptions.EqualTagIdException;
import com.oocourse.spec2.exceptions.PersonIdNotFoundException;
import com.oocourse.spec2.exceptions.RelationNotFoundException;
import com.oocourse.spec2.exceptions.TagIdNotFoundException;
import com.oocourse.spec2.exceptions.AcquaintanceNotFoundException;
import com.oocourse.spec2.exceptions.OfficialAccountIdNotFoundException;
import com.oocourse.spec2.exceptions.ArticleIdNotFoundException;
import com.oocourse.spec2.exceptions.PathNotFoundException;
import com.oocourse.spec2.exceptions.DeleteArticlePermissionDeniedException;
import com.oocourse.spec2.exceptions.DeleteOfficialAccountPermissionDeniedException;
import com.oocourse.spec2.exceptions.EqualArticleIdException;
import com.oocourse.spec2.exceptions.ContributePermissionDeniedException;
import com.oocourse.spec2.main.NetworkInterface;
import com.oocourse.spec2.main.OfficialAccountInterface;
import com.oocourse.spec2.main.PersonInterface;
import com.oocourse.spec2.main.TagInterface;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

public class Network implements NetworkInterface {
    private HashMap<Integer, PersonInterface> persons = new HashMap<>();
    // personId <-> PersonInterface
    private HashMap<Integer, OfficialAccountInterface> accounts = new HashMap<>();
    // accountId <-> OfficialAccountInterface
    private HashMap<Integer, PersonInterface> articles = new HashMap<>();
    // articleId <-> articleOwner
    private int tripleSum = 0;
    private int coupleSum = 0;
    private boolean dirtySignForCoupleSum = false;
    private HashMap<Integer, ArrayList<TagInterface>> tagMap = new HashMap<>();
    // personId <-> ArrayList<TagInterface>
    
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
            dirtySignForCoupleSum = true;
            if (tagMap.containsKey(id1) && tagMap.containsKey(id2)) {
                if (tagMap.get(id1).size() < tagMap.get(id2).size()) {
                    for (TagInterface tag : tagMap.get(id1)) {
                        if (tag.hasPerson(person2)) {
                            ((Tag) tag).addValueSum(2 * value);
                        }
                    }
                } else {
                    for (TagInterface tag : tagMap.get(id2)) {
                        if (tag.hasPerson(person1)) {
                            ((Tag) tag).addValueSum(2 * value);
                        }
                    }
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
                if (tagMap.containsKey(id1) && tagMap.containsKey(id2)) {
                    if (tagMap.get(id1).size() < tagMap.get(id2).size()) {
                        for (TagInterface tag : tagMap.get(id1)) {
                            if (tag.hasPerson(person2)) {
                                ((Tag) tag).addValueSum(2 * value);
                            }
                        }
                    } else {
                        for (TagInterface tag : tagMap.get(id2)) {
                            if (tag.hasPerson(person1)) {
                                ((Tag) tag).addValueSum(2 * value);
                            }
                        }
                    }
                }
            } else {
                checkStyle1(person1, person2, id1, id2);
                person1.modifyRelation(person2, value, false);
                person2.modifyRelation(person1, value, false);
                tripleSum -= getNumOfSameLinkedPersons(id1, id2);
            }
            dirtySignForCoupleSum = true;
        }
    }
    
    public void checkStyle1(Person person1, Person person2, int id1, int id2) {
        final int originalValue = person1.queryValue(person2);
        if (tagMap.containsKey(id1) && tagMap.containsKey(id2)) {
            if (tagMap.get(id1).size() < tagMap.get(id2).size()) {
                for (TagInterface tag : tagMap.get(id1)) {
                    if (tag.hasPerson(person2)) {
                        ((Tag) tag).addValueSum(-2 * originalValue);
                    }
                }
            } else {
                for (TagInterface tag : tagMap.get(id2)) {
                    if (tag.hasPerson(person1)) {
                        ((Tag) tag).addValueSum(-2 * originalValue);
                    }
                }
            }
        }
        if (tagMap.containsKey(id2)) {
            for (TagInterface tag : person1.getTags().values()) {
                if (tag.hasPerson(person2)) {
                    tagMap.get(id2).remove(tag);
                    if (tagMap.get(id2).isEmpty()) {
                        tagMap.remove(id2);
                        break;
                    }
                }
            }
        }
        if (tagMap.containsKey(id1)) {
            for (TagInterface tag : person2.getTags().values()) {
                if (tag.hasPerson(person1)) {
                    tagMap.get(id1).remove(tag);
                    if (tagMap.get(id1).isEmpty()) {
                        tagMap.remove(id1);
                        break;
                    }
                }
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
                if (!tagMap.containsKey(personId1)) {
                    tagMap.put(personId1, new ArrayList<>());
                }
                tagMap.get(personId1).add(getPerson(personId2).getTag(tagId));
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
            tagMap.get(personId1).remove(getPerson(personId2).getTag(tagId));
            if (tagMap.get(personId1).isEmpty()) {
                tagMap.remove(personId1);
            }
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
            for (PersonInterface person :
                ((Tag) getPerson(personId).getTag(tagId)).getPersons().values()) {
                if (tagMap.containsKey(person.getId())) {
                    tagMap.get(person.getId()).remove(getPerson(personId).getTag(tagId));
                    if (tagMap.get(person.getId()).isEmpty()) {
                        tagMap.remove(person.getId());
                    }
                }
            }
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
        PersonInterface[] personArray = new PersonInterface[persons.size()];
        int i = 0;
        for (PersonInterface person : persons.values()) {
            personArray[i] = person;
            i++;
        }
        return personArray;
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
        } else if (!isCircle(id1, id2)) {
            throw new PathNotFoundException(id1, id2);
        } else {
            if (id1 == id2) {
                return 0;
            }
            return ((Person) persons.get(id1)).getShortestPath(persons.get(id2));
        }
    }
    
    @Override
    public boolean containsAccount(int id) {
        return accounts.containsKey(id);
    }
    
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
    public boolean containsArticle(int id) {
        return articles.containsKey(id);
    }
    
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
}
