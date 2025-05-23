import com.oocourse.spec1.exceptions.*;
import com.oocourse.spec1.main.*;

import org.junit.Before;
import org.junit.Test;

import org.junit.Assume; // For assumptions if needed

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

import static org.junit.Assert.*;


// Assume MyNetwork is your concrete implementation of NetworkInterface
// and MyPerson/MyTag are its concrete implementations of PersonInterface/TagInterface
// Replace with your actual class name


public class NetworkTest {
    
    private NetworkInterface network; // Declare the interface
    
    // Use @Before to set up a fresh network instance for each test
    @Before
    public void setUp() {
        // Replace MyNetwork() with the constructor of your implementation
        network = new Network();
    }
    
    // --- queryTripleSum Tests ---
    
    @Test
    public void queryTripleSum() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        // Test case: Empty network
        assertEquals(0, network.queryTripleSum());
        
        // Test case: Less than three persons
        for (int i = 0; i < 100; i++) {
            PersonInterface p = new Person(i, "A" + i, 18);
            network.addPerson(p);
            verify(network);
        }
        PersonInterface p = new Person(-100, "A", 18);
        network.addPerson(p);
        p = new Person(-200, "A", 18);
        network.addPerson(p);
        assertEquals(0, network.queryTripleSum());
        
        // Test case: Three persons, no triangle
        network.addRelation(1, 2, 10);
        network.addRelation(2, 3, 20); // 1-2-3 form a line, not a triangle
        assertEquals(0, network.queryTripleSum());
        network.addRelation(1, 4, 20); // 1-2-3 form a line, not a triangle
        assertEquals(0, network.queryTripleSum());
        network.addRelation(3, 4, 20); // 1-2-3 form a line, not a triangle
        assertEquals(0, network.queryTripleSum());
        network.addRelation(1, 5, 20); // 1-2-3 form a line, not a triangle
        assertEquals(0, network.queryTripleSum());
        network.addRelation(5, 3, 20); // 1-2-3 form a line, not a triangle
        assertEquals(0, network.queryTripleSum());
        // Add relation to form one triangle
        network.addRelation(1, 3, 30); // Triangle 1-2-3
        assertEquals(3, network.queryTripleSum());
        
        // Test case: Four persons, one triangle
        // Test case: Four persons, two triangles sharing edge
        // Add relations to form triangle 1-2-4 as well
        network.addRelation(2, 4, 50); // Forms triangle 1-2-4
        assertEquals(5, network.queryTripleSum()); // Triangles 1-2-3 and 1-2-4
        
        
        // Test case: Four persons, two non-sharing triangles (e.g., 1-2-3 and 1-2-4)
        // This is what we have now.
        // Let's create a separate triangle 5-6-7 in a larger network scenario (omitted for brevity)
        network.modifyRelation(3, 4, 60);
        assertEquals(5, network.queryTripleSum());
        
        network.modifyRelation(3, 4, -10);
        assertEquals(5, network.queryTripleSum());
        
        network.modifyRelation(3, 4, -100);
        assertEquals(3, network.queryTripleSum());
        
        network.modifyRelation(1, 4, -100);
        assertEquals(2, network.queryTripleSum());
        
        network.modifyRelation(1, 3, -100);
        assertEquals(0, network.queryTripleSum());
        
        Random random = new Random();
        for (int i = 0; i < 100; i++) {
            boolean flag = random.nextBoolean();
            for (int j = 0; j < 100; j++) {
                if (flag) {
                    try {
                        network.addRelation(random.nextInt(100), random.nextInt(100), 10);
                    } catch (PersonIdNotFoundException | EqualRelationException e) {
                        // Ignore, we know it's not possible
                    }
                } else {
                    try {
                        network.modifyRelation(random.nextInt(100), random.nextInt(100), -30);
                    } catch (PersonIdNotFoundException | EqualPersonIdException | RelationNotFoundException e) {
                        // Ignore, we know it's not possible
                    }
                }
            }
            verify(network);
        }
    }
    
    public void verify(NetworkInterface network) {
        PersonInterface[] oldPersons = ((Network) network).getPersons();
        HashMap<Integer, PersonInterface> personsBeforeMap = new HashMap<>();
        for (PersonInterface person : oldPersons) {
            personsBeforeMap.put(person.getId(), person);
        }
        int cnt = 0;
        for (int i = 0; i < oldPersons.length; ++i) {
            for (int j = i + 1; j < oldPersons.length; ++j) {
                for (int k = j + 1; k < oldPersons.length; ++k) {
                    if (oldPersons[i].isLinked(oldPersons[j]) &&
                            oldPersons[j].isLinked(oldPersons[k]) &&
                            oldPersons[k].isLinked(oldPersons[i])) {
                        ++cnt;
                    }
                }
            }
        }
        assertEquals(cnt, network.queryTripleSum());
        PersonInterface[] newPersons = ((Network) network).getPersons();
        assertEquals(oldPersons.length, newPersons.length);
        for (PersonInterface person : newPersons) {
            assertTrue(personsBeforeMap.containsKey(person.getId()));
            assertTrue(((Person) person).strictEquals(personsBeforeMap.get(person.getId())));
        }
    }
    
    @Test
    public void testMinusId() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        Person person = new Person(-1, "A", 18);
        network.addPerson(person);
        Person person2 = new Person(-2, "B", 18);
        network.addPerson(person2);
        network.addRelation(person.getId(), person2.getId(), 10);
        assertEquals(0, network.queryTripleSum());
        Person person3 = new Person(-3, "C", 18);
        network.addPerson(person3);
        network.addRelation(person.getId(), person3.getId(), 10);
        assertEquals(0, network.queryTripleSum());
        network.addRelation(person2.getId(), person3.getId(), 10);
        assertEquals(1, network.queryTripleSum());
        network.modifyRelation(person.getId(), person2.getId(), -100);
        assertEquals(0, network.queryTripleSum());
        network.modifyRelation(person.getId(), person3.getId(), -100);
        assertEquals(0, network.queryTripleSum());
        network.modifyRelation(person2.getId(), person3.getId(), -100);
        assertEquals(0, network.queryTripleSum());
    }
    
    @Test
    public void test1() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        PersonInterface person1 = new Person(1, "A", 20);
        PersonInterface person2 = new Person(2, "B", 21);
        PersonInterface person3 = new Person(3, "C", 22);
        network.addPerson(person1);
        network.addPerson(person2);
        network.addPerson(person3);
        network.addRelation(1, 2, 10);
        network.addRelation(2, 3, 10);
        network.addRelation(3, 1, 10);
        PersonInterface person4 = new Person(4, "D", 23);
        network.addPerson(person4);
        network.addRelation(2, 4, 10);
        network.addRelation(4, 3, 10);
        
        assertEquals(2, network.queryTripleSum());
        network.addRelation(4, 1, 10);
        assertEquals(4, network.queryTripleSum());
        network.modifyRelation(2, 3, -20);
        assertEquals(2, network.queryTripleSum());
        network.modifyRelation(1, 2, -20);
        assertEquals(1, network.queryTripleSum());
        network.modifyRelation(1, 3, -20);
        assertEquals(0, network.queryTripleSum());
        network.modifyRelation(2, 4, -20);
        assertEquals(0, network.queryTripleSum());
        network.modifyRelation(4, 3, -20);
        assertEquals(0, network.queryTripleSum());
        network.modifyRelation(1, 4, -20);
        assertEquals(0, network.queryTripleSum());
        try {
            network.modifyRelation(3, 4, -20);
        } catch (RelationNotFoundException e) {
            // Ignore, we know it's not possible
        }
        assertEquals(0, network.queryTripleSum());
    }
    
    @Test
    public void test2() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        PersonInterface person1 = new Person(1, "A", 20);
        PersonInterface person2 = new Person(2, "B", 21);
        PersonInterface person3 = new Person(3, "C", 22);
        network.addPerson(person1);
        network.addPerson(person2);
        network.addPerson(person3);
        network.addRelation(1, 2, 10);
        network.addRelation(2, 3, 10);
        network.addRelation(3, 1, 10);
        PersonInterface person4 = new Person(4, "D", 23);
        network.addPerson(person4);
        network.addRelation(2, 4, 10);
        network.addRelation(4, 3, 10);
        
        assertEquals(2, network.queryTripleSum());
        network.modifyRelation(1, 3, -17);
        
        int result = network.queryTripleSum();
        assertEquals(1, result);
        result = network.queryTripleSum();
        assertEquals(1, result);
        
        network.modifyRelation(4, 3, -7);
        result = network.queryTripleSum();
        assertEquals(1, result);
        network.modifyRelation(4, 3, -7);
        result = network.queryTripleSum();
        assertEquals(0, result);
    }
    
    @Test
    public void test3() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        PersonInterface person1 = new Person(1, "A", 20);
        PersonInterface person2 = new Person(2, "B", 21);
        PersonInterface person3 = new Person(3, "C", 22);
        network.addPerson(person1);
        network.addPerson(person2);
        network.addPerson(person3);
        network.addRelation(1, 2, 10);
        network.addRelation(2, 3, 10);
        network.addRelation(3, 1, 10);
        PersonInterface person4 = new Person(0, "David", 23);
        PersonInterface person5 = new Person(-1, "Alice", 20);
        network.addPerson(person4);
        network.addPerson(person5);
        network.modifyRelation(1, 3, -17);
        network.addRelation(2, 0, 10);
        network.addRelation(-1, 0, 10);
        int result = network.queryTripleSum();
        assertEquals(0, result);
        // 移除一个关系，减少三元组数量
        network.addRelation(2, -1, 10);
        
        
        result = network.queryTripleSum();
        assertEquals(1, result);
        result = network.queryTripleSum();
        assertEquals(1, result);
        result = network.queryTripleSum();
        assertEquals(1, result);
    }
    
    @Test
    public void test4() throws EqualPersonIdException, PersonIdNotFoundException, EqualRelationException, RelationNotFoundException {
        PersonInterface person1 = new Person(1, "A", 20);
        PersonInterface person2 = new Person(2, "B", 21);
        PersonInterface person3 = new Person(3, "C", 22);
        network.addPerson(person1);
        network.addPerson(person2);
        network.addPerson(person3);
        network.addRelation(1, 2, 10);
        network.addRelation(2, 3, 10);
        network.addRelation(3, 1, 10);
        PersonInterface person4 = new Person(4, "David", 23);
        network.addPerson(person4);
        network.addRelation(2, 4, 10);
        network.addRelation(4, 3, 10);
        int expected = 2;
        int result = network.queryTripleSum();
        assertEquals(expected, result);
        // 移除一个关系，减少三元组数量
        network.modifyRelation(2, 3, -2);
        assertEquals(2, network.queryTripleSum());
        network.modifyRelation(2, 3, -20);
        assertEquals(0, network.queryTripleSum());
        verify(network);
        verify(network);
        verify(network);
        verify(network);
        verify(network);
    }
}