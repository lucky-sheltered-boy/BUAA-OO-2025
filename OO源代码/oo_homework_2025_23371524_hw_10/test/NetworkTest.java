import com.oocourse.spec2.exceptions.*;
import com.oocourse.spec2.main.*; // Import the interfaces
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

import java.util.*;

public class NetworkTest {
    
    private NetworkInterface network;
    private NetworkInterface network2;
    PersonInterface[] beforePersons;
    PersonInterface[] afterPersons;
    
    // Use the provided implementations as collaborators
    private Person createPerson(int id, String name, int age) {
        return new Person(id, name, age);
    }
    
    private boolean isPure(PersonInterface[] before, PersonInterface[] after) {
        if (before.length!= after.length) {
            return false;
        }
        HashMap<Integer, PersonInterface> beforeMap = new HashMap<>();
        for (PersonInterface person : before) {
            beforeMap.put(person.getId(), person);
        }
        HashMap<Integer, PersonInterface> afterMap = new HashMap<>();
        for (PersonInterface person : after) {
            afterMap.put(person.getId(), person);
        }
        if (beforeMap.size() != afterMap.size()) {
            return false;
        }
        for (int id : beforeMap.keySet()) {
            if (!afterMap.containsKey(id)) {
                return false;
            }
            if (!((Person) beforeMap.get(id)).strictEquals(afterMap.get(id))) {
                return false;
            }
        }
        return true;
    }
    
    private void check(int expected) {
        beforePersons = ((Network) network2).getPersons();
        assertEquals(expected, network.queryCoupleSum());
        afterPersons = ((Network) network).getPersons();
        assertTrue(isPure(beforePersons, afterPersons));
        assertEquals(expected, network.queryCoupleSum());
        assertEquals(expected, network2.queryCoupleSum());
    }
    
    @Before
    public void setUp() {
        network = new Network(); // Create a fresh network for each test
        network2 = new Network(); // Create a fresh network for each test
    }
    
    // --- queryCoupleSum Tests ---
    @Test
    public void testQueryCoupleSum_EmptyNetwork() {
        check(0);
    }
    
    @Test
    public void testQueryCoupleSum_NoCouples() throws Exception {
        Person p1 = createPerson(1, "A", 10);
        Person p2 = createPerson(2, "B", 20);
        Person p3 = createPerson(3, "C", 30);
        Person p11 = createPerson(1,"A",10);
        Person p22 = createPerson(2,"B",20);
        Person p33 = createPerson(3,"C",30);
        check(0);
        network.addPerson(p1);
        network.addPerson(p2);
        network.addPerson(p3);
        network2.addPerson(p11);
        network2.addPerson(p22);
        network2.addPerson(p33);
        check(0);
        network.addRelation(1, 2, 10); // p1 best is p2 (only link)
        network2.addRelation(1, 2, 10); // p1 best is p2 (only link)
        check(1);
        network.addRelation(2, 3, 10); // p2 best is p3 (only link)
        network.addRelation(1, 3, 10); // p1 best is p3 (tie)
        network2.addRelation(2, 3, 10); // p2 best is p3 (only link)
        network2.addRelation(1, 3, 10); // p1 best is p3 (tie)
        // p1's best is p2, p2's best is p3. Not a couple.
        check(1);
    }
    
    @Test
    public void testQueryCoupleSum_OneCouple() throws Exception {
        Person p1 = createPerson(1, "A", 10);
        Person p2 = createPerson(2, "B", 20);
        Person p3 = createPerson(3, "C", 30);
        Person p11 = createPerson(1,"A",10);
        Person p22 = createPerson(2,"B",20);
        Person p33 = createPerson(3,"C",30);
        check(0);
        network.addPerson(p1);
        network.addPerson(p2);
        network.addPerson(p3);
        network2.addPerson(p11);
        network2.addPerson(p22);
        network2.addPerson(p33);
        check(0);
        network.addRelation(1, 2, 20); // p1-p2 value 20
        network.addRelation(1, 3, 10); // p1-p3 value 10 -> p1's best is p2
        network.addRelation(2, 3, 15); // p2-p3 value 15 -> p2's best is p1 (value 20 > 15)
        network2.addRelation(1, 2, 20); // p1-p2 value 20
        network2.addRelation(1, 3, 10); // p1-p3 value 10 -> p1's best is p2
        network2.addRelation(2, 3, 15); // p2-p3 value 15 -> p2's best is p1 (value 20 > 15)
        // p1's best is p2 (value 20 > 10). p2's best is p1 (value 20 > 15). They are a couple.
        check(1);
        
        // Add another person, make them best of p3, shouldn't affect the p1-p2 couple
        Person p4 = createPerson(4, "D", 40);
        Person p44 = createPerson(4,"D",40);
        network.addPerson(p4);
        network2.addPerson(p44);
        network.addRelation(3, 4, 100); // p3's best is now p4
        network2.addRelation(3, 4, 100); // p3's best is now p4
        check(2);
        network.modifyRelation(1, 3, 50);
        network2.modifyRelation(1, 3, 50);
        check(1);
        network.addPerson(createPerson(5, "E", 50));
        network2.addPerson(createPerson(5, "E", 50));
        network.addPerson(createPerson(6, "F", 60));
        network2.addPerson(createPerson(6, "F", 60));
        network.addRelation(5, 6, 100); // p5's best is now p6
        network2.addRelation(5, 6, 100); // p5's best is now p6
        check(2);
        network.addRelation(1, 5, 1000);
        network2.addRelation(1, 5, 1000); // p1's best is now p5
        check(2);
        
    }
    
    @Test
    public void testQueryCoupleSum_MultipleCouples() throws Exception {
        Person p1 = createPerson(1, "A", 10);
        Person p2 = createPerson(2, "B", 20);
        Person p3 = createPerson(3, "C", 30);
        Person p4 = createPerson(4, "D", 40);
        Person p11 = createPerson(1,"A",10);
        Person p22 = createPerson(2,"B",20);
        Person p33 = createPerson(3,"C",30);
        Person p44 = createPerson(4,"D",40);
        check(0);
        network.addPerson(p1);
        network.addPerson(p2);
        network.addPerson(p3);
        network.addPerson(p4);
        network2.addPerson(p11);
        network2.addPerson(p22);
        network2.addPerson(p33);
        network2.addPerson(p44);
        check(0);
        network.addRelation(1, 2, 10); // p1 best = p2, p2 best = p1. Couple (1,2)
        network.addRelation(3, 4, 20); // p3 best = p4, p4 best = p3. Couple (3,4)
        network2.addRelation(1, 2, 10); // p1 best = p2, p2 best = p1. Couple (1,2)
        network2.addRelation(3, 4, 20); // p3 best = p4, p4 best = p3. Couple (3,4)
        check(2);
    }
    
    @Test
    public void testQueryCoupleSum_ModifyRelationBreaksCouple() throws Exception {
        Person p1 = createPerson(1, "A", 10);
        Person p2 = createPerson(2, "B", 20);
        Person p3 = createPerson(3, "C", 30);
        Person p11 = createPerson(1,"A",10);
        Person p22 = createPerson(2,"B",20);
        Person p33 = createPerson(3,"C",30);
        check(0);
        network.addPerson(p1);
        network.addPerson(p2);
        network.addPerson(p3);
        network2.addPerson(p11);
        network2.addPerson(p22);
        network2.addPerson(p33);
        network.addRelation(1, 2, 20); // p1-p2 value 20
        network.addRelation(1, 3, 10); // p1-p3 value 10 -> p1 best = p2
        network.addRelation(2, 3, 15); // p2-p3 value 15 -> p2 best = p1
        network2.addRelation(1, 2, 20); // p1-p2 value 20
        network2.addRelation(1, 3, 10); // p1-p3 value 10 -> p1 best = p2
        network2.addRelation(2, 3, 15); // p2-p3 value 15 -> p2 best = p1
        check(1);
        
        // Modify relation 1-3 so p1's best becomes p3
        network.modifyRelation(1, 3, 30);
        // New value 10+15 = 25. p1 best is now p3 (25 > 20).
        network2.modifyRelation(1, 3, 30);
        check(1);
    }
    
    @Test
    public void test1() throws Exception {
        Person p1 = createPerson(1, "A", 10);
        Person p2 = createPerson(2, "B", 20);
        Person p3 = createPerson(3, "C", 30);
        Person p4 = createPerson(4, "D", 40);
        Person p5 = createPerson(5, "E", 50);
        Person p11 = createPerson(1,"A",10);
        Person p22 = createPerson(2,"B",20);
        Person p33 = createPerson(3,"C",30);
        Person p44 = createPerson(4,"D",40);
        Person p55 = createPerson(5,"E",50);
        check(0);
        network.addPerson(p1);
        network.addPerson(p2);
        network.addPerson(p3);
        network.addPerson(p4);
        network.addPerson(p5);
        network2.addPerson(p11);
        network2.addPerson(p22);
        network2.addPerson(p33);
        network2.addPerson(p44);
        network2.addPerson(p55);
        check(0);
        
        network.addRelation(1, 5, 10); // p1 best = p2, p2 best = p1. Couple (1,2)
        network.addRelation(1, 3, 5); // p3 best = p4, p4 best = p3. Couple (3,4)
        network.addRelation(5, 4, 20); // p1 best = p2, p2 best = p1. Couple (1,2)
        network.addRelation(4, 3, 25); // p2 best = p1, p1 best = p2. Couple (2,3)
        network.addRelation(2, 3, 30); // p2 best = p1, p1 best = p2. Couple (2,3)
        network2.addRelation(1, 5, 10); // p1 best = p2, p2 best = p1. Couple (1,2)
        network2.addRelation(1, 3, 5); // p3 best = p4, p4 best = p3. Couple (3,4)
        network2.addRelation(5, 4, 20); // p1 best = p2, p2 best = p1. Couple (1,2)
        network2.addRelation(4, 3, 25); // p2 best = p1, p1 best = p2. Couple (2,3)
        network2.addRelation(2, 3, 30); // p2 best = p1, p1 best = p2. Couple (2,3)
        check(1);
        network.modifyRelation(1, 5, 20); // New value 10+15 = 25. p1 best is now p3 (25 > 20).
        network2.modifyRelation(1, 5, 20); // New value 10+15 = 25. p1 best is now p3 (25 > 20).
        check(2);
        check(2);
    }
}