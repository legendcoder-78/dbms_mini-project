import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database connection helper
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    tag_filter = request.args.get('tag')
    db = get_db_connection()
    cur = db.cursor()
    
    # Advanced Object Use: Querying from PostSummaryView
    if tag_filter:
        # Filter posts using the View but joining for strict tag matching
        query = """
            SELECT v.* 
            FROM PostSummaryView v
            JOIN Post_Tags pt ON v.id = pt.post_id 
            JOIN Tags t ON pt.tag_id = t.id 
            WHERE t.name = %s 
            ORDER BY v.created_at DESC
        """
        cur.execute(query, (tag_filter,))
    else:
        query = "SELECT * FROM PostSummaryView ORDER BY created_at DESC"
        cur.execute(query)
    
    posts = cur.fetchall()

    # Complex Query 2 (Aggregate): Top 3 most used tags
    cur.execute("""
        SELECT Tags.name, COUNT(Post_Tags.post_id) as post_count 
        FROM Tags 
        JOIN Post_Tags ON Tags.id = Post_Tags.tag_id 
        GROUP BY Tags.id, Tags.name 
        ORDER BY post_count DESC LIMIT 3
    """)
    top_tags = cur.fetchall()

    # Complex Query 3 (Subquery): Users who have written more than the average number of posts
    cur.execute("""
        SELECT username, COUNT(Posts.id) as post_count
        FROM Users
        JOIN Posts ON Users.id = Posts.user_id
        GROUP BY Users.id, Users.username
        HAVING COUNT(Posts.id) > (
            SELECT AVG(post_count) FROM (
                SELECT COUNT(id) as post_count FROM Posts GROUP BY user_id
            ) as avg_posts
        )
    """)
    active_users = cur.fetchall()

    # Complex Query 4 (Engagement Insights): Average number of tags per post
    cur.execute("""
        SELECT AVG(tag_count) as avg_tags FROM (
            SELECT COUNT(tag_id) as tag_count FROM Post_Tags GROUP BY post_id
        ) as counts
    """)
    avg_tags_result = cur.fetchone()
    avg_tags = round(avg_tags_result['avg_tags'], 2) if avg_tags_result and avg_tags_result['avg_tags'] else 0

    # Complex Query 5 (Unused Data Search): Inactive Tags
    cur.execute("""
        SELECT name FROM Tags 
        WHERE id NOT IN (SELECT tag_id FROM Post_Tags)
    """)
    inactive_tags = cur.fetchall()
    
    cur.close()
    db.close()

    return render_template('index.html', 
                           posts=posts, 
                           top_tags=top_tags, 
                           active_users=active_users, 
                           avg_tags=avg_tags,
                           inactive_tags=inactive_tags,
                           current_tag=tag_filter)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        db = get_db_connection()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s)", 
                        (username, email, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"Error: {e}"
        finally:
            cur.close()
            db.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        cur = db.cursor()
        cur.execute("SELECT id, username, password_hash FROM Users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return "Invalid username or password"
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags_raw = request.form.get('tags', '')
        user_id = session['user_id']
        
        db = get_db_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO Posts (title, content, user_id) VALUES (%s, %s, %s)", (title, content, user_id))
        post_id = db.insert_id()
        
        if tags_raw:
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
            for tag_name in tags:
                cur.execute("SELECT id FROM Tags WHERE name = %s", (tag_name,))
                tag_result = cur.fetchone()
                
                if tag_result:
                    tag_id = tag_result['id']
                else:
                    cur.execute("INSERT INTO Tags (name) VALUES (%s)", (tag_name,))
                    tag_id = db.insert_id()
                
                cur.execute("INSERT INTO Post_Tags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))
        
        db.commit()
        cur.close()
        db.close()
        return redirect(url_for('index'))
    
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
