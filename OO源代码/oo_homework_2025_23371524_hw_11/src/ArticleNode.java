public class ArticleNode {
    private int articleId;
    private ArticleNode prev;
    private ArticleNode next;
    
    public ArticleNode(int articleId) {
        this.articleId = articleId;
        this.prev = null;
        this.next = null;
    }
    
    public int getArticleId() {
        return articleId;
    }
    
    public ArticleNode getPrev() {
        return prev;
    }
    
    public void setPrev(ArticleNode prev) {
        this.prev = prev;
    }
    
    public ArticleNode getNext() {
        return next;
    }
    
    public void setNext(ArticleNode next) {
        this.next = next;
    }
}
