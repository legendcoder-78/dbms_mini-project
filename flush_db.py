import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def flush_db():
    try:
        # Connect to MySQL server
        db = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        cursor = db.cursor()

        print("Flushing database data...")

        # Disable foreign key checks to allow truncation in any order
        # and ensure a clean wipe without constraint errors.
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # Truncate tables to remove all data and reset Auto-Increment IDs
        cursor.execute("TRUNCATE TABLE Post_Tags;")
        cursor.execute("TRUNCATE TABLE Posts;")
        cursor.execute("TRUNCATE TABLE Users;")
        
        # Note: We are keeping the Tags table as requested.
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        db.commit()
        print("Successfully wiped Users, Posts, and Post_Tags data.")
        print("You can now register a new admin account.")

    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    # Safety confirmation
    confirm = input("Are you sure you want to wipe all user and post data? (y/n): ")
    if confirm.lower() == 'y':
        flush_db()
    else:
        print("Operation cancelled.")
