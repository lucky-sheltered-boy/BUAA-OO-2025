import com.oocourse.spec2.main.OfficialAccountInterface;
import com.oocourse.spec2.main.PersonInterface;

import java.util.HashMap;

public class OfficialAccount implements OfficialAccountInterface {
    private int ownerId;
    private int id;
    private String name;
    private HashMap<Integer, PersonInterface> followers = new HashMap<>();
    // personId <--> PersonInterface
    private HashMap<Integer, Integer> contributions = new HashMap<>();
    // personId <--> contributions
    private HashMap<Integer, PersonInterface> articles = new HashMap<>();
    // articleId <--> articleOwner
    private int bestContributorid = -1;
    private int bestContributorValue = Integer.MIN_VALUE;
    
    public OfficialAccount(int ownerId, int id, String name) {
        this.ownerId = ownerId;
        this.id = id;
        this.name = name;
    }
    
    @Override
    public int getOwnerId() {
        return ownerId;
    }
    
    @Override
    public void addFollower(PersonInterface person) {
        if (!containsFollower(person)) {
            followers.put(person.getId(), person);
            contributions.put(person.getId(), 0);
            if (0 > bestContributorValue ||
                0 == bestContributorValue && person.getId() < bestContributorid) {
                bestContributorValue = 0;
                bestContributorid = person.getId();
            }
        }
    }
    
    @Override
    public boolean containsFollower(PersonInterface person) {
        if (person == null) {
            return false;
        }
        return followers.containsKey(person.getId());
    }
    
    @Override
    public void addArticle(PersonInterface person, int id) {
        if (!containsArticle(id) && containsFollower(person)) {
            articles.put(id, person);
            contributions.put(person.getId(), contributions.get(person.getId()) + 1);
            if (contributions.get(person.getId()) > bestContributorValue ||
                contributions.get(person.getId()) == bestContributorValue &&
                person.getId() < bestContributorid) {
                bestContributorValue = contributions.get(person.getId());
                bestContributorid = person.getId();
            }
        }
    }
    
    @Override
    public boolean containsArticle(int id) {
        return articles.containsKey(id);
    }
    
    @Override
    public void removeArticle(int id) {
        if (containsArticle(id)) {
            articles.remove(id);
        }
    }
    
    @Override
    public int getBestContributor() {
        return bestContributorid;
    }
    
    public void addArticleToAllFollowers(int articleId) {
        for (PersonInterface person : followers.values()) {
            ((Person) person).addArticleToFirst(articleId);
        }
    }
    
    public void delArticle(int articleId) {
        for (PersonInterface person : followers.values()) {
            ((Person) person).delArticle(articleId);
        }
        PersonInterface articleOwner = articles.get(articleId);
        if (articleOwner != null) {
            contributions.put(articleOwner.getId(), contributions.get(articleOwner.getId()) - 1);
        }
        articles.remove(articleId);
        if (articleOwner != null && articleOwner.getId() == bestContributorid) {
            bestContributorValue = Integer.MIN_VALUE;
            bestContributorid = -1;
            for (int id : contributions.keySet()) {
                if (contributions.get(id) > bestContributorValue ||
                    contributions.get(id) == bestContributorValue && id < bestContributorid) {
                    bestContributorValue = contributions.get(id);
                    bestContributorid = id;
                }
            }
        }
    }
}
