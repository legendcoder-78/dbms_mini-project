# Blog Management System

A full-stack Blog Management System built with **Flask**, **MySQL (PyMySQL)**, and **HTML/CSS**. This project demonstrates core DBMS concepts including 3NF schema design, complex JOINs, aggregations, subqueries, and database triggers.

## 🚀 Present Capabilities
- **Secure User Authentication**: Users can register and log in. Passwords are encrypted using Werkzeug's security hashing.
- **Session Management**: Uses `Flask-Session` to keep users logged in across the site.
- **Blog Post Creation**: Logged-in users can create posts with titles, content, and tags.
- **M:N Tagging System**: Posts can have multiple tags, and tags can belong to multiple posts.
- **Dynamic Search**: Filter the blog feed by specific tags using a 3-way JOIN query.
- **Automated Metadata**: A database trigger automatically tracks the last modification time of every post.
- **Dynamic Content Moderation**: A database-centric system that blocks inappropriate content using a `Blacklist` table and a `BEFORE INSERT` trigger.
- **Data Insights**: 
    - Real-time aggregation of the most popular tags.
    - Subquery-based identification of highly active users (authors with above-average post counts).

## 🛠 Tech Stack
- **Backend**: Python, Flask
- **Database**: MySQL
- **DB Connector**: PyMySQL (Pure Python, macOS compatible)
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Environment**: python-dotenv, Flask-Session

## 📊 SQL Objects & Queries
The system utilizes advanced database objects and queries to manage data:

1.  **Database View (`PostSummaryView`)**:
    Centralizes post data, author info, and tag lists into a single queryable object for efficiency.

2.  **Dynamic Moderation Trigger (`validate_post_content`)**:
    Blocks posts containing prohibited words stored in the `Blacklist` table.
    ```sql
    CREATE TRIGGER validate_post_content BEFORE INSERT ON Posts
    FOR EACH ROW
    BEGIN
        IF EXISTS (
            SELECT 1 FROM Blacklist 
            WHERE NEW.title LIKE CONCAT('%', bad_word, '%') 
               OR NEW.content LIKE CONCAT('%', bad_word, '%')
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Content violation: Vulgar language detected.';
        END IF;
    END;
    ```

3.  **Metadata Tracking Trigger (`update_post_last_modified`)**:
    ```sql
    CREATE TRIGGER update_post_last_modified BEFORE UPDATE ON Posts
    FOR EACH ROW SET NEW.LastModified = CURRENT_TIMESTAMP;
    ```

4.  **Aggregation (Top Tags)**:
    ```sql
    SELECT Tags.name, COUNT(Post_Tags.post_id) FROM Tags 
    JOIN Post_Tags ON Tags.id = Post_Tags.tag_id 
    GROUP BY Tags.id ORDER BY COUNT(*) DESC LIMIT 3;
    ```

5.  **Subquery (Active Users)**:
    ```sql
    SELECT username FROM Users WHERE id IN (
        SELECT user_id FROM Posts GROUP BY user_id 
        HAVING COUNT(*) > (SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM Posts GROUP BY user_id) as avg_tbl)
    );
    ```

## ⚙️ How to Run

1.  **Start MySQL Server**:
    Ensure your local MySQL server is running.

2.  **Configuration**:
    Update the `.env` file with your `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB`.

3.  **Initialize Environment**:
    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Setup Database**:
    ```bash
    python init_db.py
    ```
    *Note: This will create the schema, views, triggers, and seed the moderation blacklist.*

5.  **Start Application**:
    ```bash
    python app.py
    ```
    Visit `http://127.0.0.1:5000` in your browser.
