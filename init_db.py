import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def init_db():
    try:
        # Connect to MySQL server
        db = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        cursor = db.cursor()

        # Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Blacklist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Blacklist (
                bad_word VARCHAR(50) PRIMARY KEY
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Seed Blacklist with sample rows
        cursor.execute("INSERT IGNORE INTO Blacklist (bad_word) VALUES ('spamword1'), ('spamword2')")

        # Create Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
            )
        """)

        # Create Trigger for LastModified
        # Note: We use DROP TRIGGER IF EXISTS to allow re-running the script
        cursor.execute("DROP TRIGGER IF EXISTS update_post_last_modified")
        cursor.execute("""
            CREATE TRIGGER update_post_last_modified
            BEFORE UPDATE ON Posts
            FOR EACH ROW
            SET NEW.LastModified = CURRENT_TIMESTAMP;
        """)

        # Create Trigger for Content Validation (Dynamic Blacklist)
        cursor.execute("DROP TRIGGER IF EXISTS validate_post_content")
        cursor.execute("""
            CREATE TRIGGER validate_post_content
            BEFORE INSERT ON Posts
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
        """)

        # Create Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """)

        # Create Post_Tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Post_Tags (
                post_id INT,
                tag_id INT,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES Posts(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
            )
        """)

        # Advanced Object (Database View): PostSummaryView
        # Performs a 3-way JOIN and groups tags into a comma-separated list
        cursor.execute("""
            CREATE OR REPLACE VIEW PostSummaryView AS
            SELECT 
                p.id, 
                p.title, 
                p.content, 
                p.created_at, 
                u.username, 
                GROUP_CONCAT(t.name ORDER BY t.name ASC SEPARATOR ', ') as tag_list
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            LEFT JOIN Post_Tags pt ON p.id = pt.post_id
            LEFT JOIN Tags t ON pt.tag_id = t.id
            GROUP BY p.id;
        """)

        db.commit()
        print("Database initialized successfully!")

    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    init_db()
