import com.oocourse.spec3.main.Runner;

public class MainClass {
    public static void main(String[] args) throws Exception {
        Runner runner = new Runner(Person.class, Network.class, Tag.class, Message.class,
            EmojiMessage.class, ForwardMessage.class, RedEnvelopeMessage.class);
        runner.run();
    }
}
