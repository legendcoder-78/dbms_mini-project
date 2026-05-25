# Blog Management System

A full-stack Blog Management System built with **Flask**, **MySQL (PyMySQL)**, and **HTML/CSS**. This project demonstrates core DBMS concepts including 3NF schema design, complex JOINs, aggregations, subqueries, and database triggers.

## 🚀 Present Capabilities
- **Secure User Authentication**: Users can register and log in. Passwords are encrypted using Werkzeug's security hashing.
- **Session Management**: Uses `Flask-Session` to keep users logged in across the site.
- **Blog Post Creation**: Logged-in users can create posts with titles, content, and tags.
- **M:N Tagging System**: Posts can have multiple tags, and tags can belong to multiple posts.
- **Dynamic Search**: Filter the blog feed by specific tags using a 3-way JOIN query.
- **Automated Metadata**: A database trigger automatically tracks the last modification time of every post.
- **Data Insights**: 
    - Real-time aggregation of the most popular tags.
    - Subquery-based identification of highly active users (authors with above-average post counts).

## 🛠 Tech Stack
- **Backend**: Python, Flask
- **Database**: MySQL
- **DB Connector**: PyMySQL (Pure Python, macOS compatible)
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Environment**: python-dotenv, Flask-Session

## 📊 SQL Queries Executed
The system executes several complex queries to manage data:
1.  **3-Way JOIN (Search)**:
    ```sql
    SELECT Posts.*, Users.username FROM Posts 
    JOIN Users ON Posts.user_id = Users.id 
    JOIN Post_Tags ON Posts.id = Post_Tags.post_id 
    JOIN Tags ON Post_Tags.tag_id = Tags.id 
    WHERE Tags.name = %s;
    ```
2.  **Aggregation (Top Tags)**:
    ```sql
    SELECT Tags.name, COUNT(Post_Tags.post_id) FROM Tags 
    JOIN Post_Tags ON Tags.id = Post_Tags.tag_id 
    GROUP BY Tags.id ORDER BY COUNT(*) DESC LIMIT 3;
    ```
3.  **Subquery (Active Users)**:
    ```sql
    SELECT username FROM Users WHERE id IN (
        SELECT user_id FROM Posts GROUP BY user_id 
        HAVING COUNT(*) > (SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM Posts GROUP BY user_id) as avg_tbl)
    );
    ```
4.  **Database Trigger**:
    ```sql
    CREATE TRIGGER update_post_last_modified BEFORE UPDATE ON Posts
    FOR EACH ROW SET NEW.LastModified = CURRENT_TIMESTAMP;
    ```

## ⚙️ How to Run

1.  **Start MySQL Server**:
    Ensure your local MySQL server is running (e.g., `brew services start mysql`).

2.  **Configuration**:
    Update the `.env` file wi th your `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB`.

3.  **Initialize Environment**:
    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Setup Database**:
    ```bash
    python init_db.py
    ```

5.  **Start Application**:
    ```bash
    flask run
    ```
    Visit `http://127.0.0.1:5000` in your browser.
