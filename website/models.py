from . import get_db_connection

# ------------------------------
# User functions
# ------------------------------
def insert_user(first_name, last_name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user (first_name, last_name, email, password, date_joined) VALUES (%s, %s, %s, %s, NOW())",
        (first_name, last_name, email, password)
    )
    conn.commit()
    conn.close()


def update_user(user_id, fields):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_string = ", ".join([f"{k}=%s" for k in fields.keys()])
    values = list(fields.values())
    values.append(user_id)
    cursor.execute(f"UPDATE user SET {set_string} WHERE id=%s", values)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


# ------------------------------
# Post functions
# ------------------------------
def create_post(title, content, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO post (title, content, date, user_id) VALUES (%s, %s, NOW(), %s)",
        (title, content, user_id)
    )
    conn.commit()
    conn.close()


def create_post_with_image(title, content, user_id, image=None, category=None, tags=None, is_draft=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Debug: Print what we're inserting
    print(f"DEBUG MODEL: Inserting post with image: {image}")
    print(f"DEBUG MODEL: Title: {title}, Content: {content[:50] if content else 'None'}...")
    
    try:
        cursor.execute(
            "INSERT INTO post (title, content, image, category, tags, drafts, date, user_id) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)",
            (title, content, image, category, tags, is_draft, user_id)
        )
        conn.commit()
        print(f"DEBUG MODEL: Post inserted successfully with ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"DEBUG MODEL: Error inserting post: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_user_posts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE user_id=%s ORDER BY date DESC", (user_id,))
    posts = cursor.fetchall()
    conn.close()
    return posts


def get_post_by_id(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    conn.close()
    return post


def get_post_comments(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comment WHERE post_id=%s", (post_id,))
    comments = cursor.fetchall()
    conn.close()
    return comments


# ------------------------------
# Like / Dislike
# ------------------------------
def like_post(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `like` (user_id, post_id) VALUES (%s,%s)", (user_id, post_id))
    conn.commit()
    conn.close()


def dislike_post(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dislike (user_id, post_id) VALUES (%s,%s)", (user_id, post_id))
    conn.commit()
    conn.close()


# ------------------------------
# Comments & Replies
# ------------------------------
def add_comment(user_id, post_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comment (user_id, post_id, data, date) VALUES (%s, %s, %s, NOW())",
        (user_id, post_id, data)
    )
    conn.commit()
    conn.close()


def reply_to_comment(user_id, comment_id, post_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reply_comment (user_id, comment_id, post_id, data, date) VALUES (%s, %s, %s, %s, NOW())",
        (user_id, comment_id, post_id, data)
    )
    conn.commit()
    conn.close()


def like_comment(user_id, post_id, comment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comment_like (user_id, post_id, comment_id) VALUES (%s,%s,%s)",
        (user_id, post_id, comment_id)
    )
    conn.commit()
    conn.close()


# ------------------------------
# Friend Request functions
# ------------------------------
def send_friend_request(sender_id, receiver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if request already exists
    cursor.execute(
        "SELECT * FROM friend_request WHERE sender_id=%s AND receiver_id=%s",
        (sender_id, receiver_id)
    )
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute(
            "INSERT INTO friend_request (sender_id, receiver_id, status, date_sent) VALUES (%s, %s, 'pending', NOW())",
            (sender_id, receiver_id)
        )
        conn.commit()
    conn.close()
    return not existing


def accept_friend_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the request details
    cursor.execute("SELECT * FROM friend_request WHERE id=%s", (request_id,))
    request = cursor.fetchone()
    
    if request:
        # Update request status
        cursor.execute(
            "UPDATE friend_request SET status='accepted', date_responded=NOW() WHERE id=%s",
            (request_id,)
        )
        
        # Add friendship both ways
        cursor.execute(
            "INSERT INTO friendship (user1_id, user2_id, date_created) VALUES (%s, %s, NOW())",
            (request['sender_id'], request['receiver_id'])
        )
        cursor.execute(
            "INSERT INTO friendship (user1_id, user2_id, date_created) VALUES (%s, %s, NOW())",
            (request['receiver_id'], request['sender_id'])
        )
        
        conn.commit()
    conn.close()


def reject_friend_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE friend_request SET status='rejected', date_responded=NOW() WHERE id=%s",
        (request_id,)
    )
    conn.commit()
    conn.close()


def get_pending_friend_requests(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT fr.*, u.first_name, u.last_name, u.email 
           FROM friend_request fr 
           JOIN user u ON fr.sender_id = u.id 
           WHERE fr.receiver_id=%s AND fr.status='pending'
           ORDER BY fr.date_sent DESC""",
        (user_id,)
    )
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_sent_friend_requests(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT fr.*, u.first_name, u.last_name, u.email 
           FROM friend_request fr 
           JOIN user u ON fr.receiver_id = u.id 
           WHERE fr.sender_id=%s AND fr.status='pending'
           ORDER BY fr.date_sent DESC""",
        (user_id,)
    )
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_user_friends(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.* FROM user u 
           JOIN friendship f ON u.id = f.user2_id 
           WHERE f.user1_id = %s
           ORDER BY u.first_name, u.last_name""",
        (user_id,)
    )
    friends = cursor.fetchall()
    conn.close()
    return friends


def are_friends(user1_id, user2_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM friendship WHERE user1_id=%s AND user2_id=%s",
        (user1_id, user2_id)
    )
    friendship = cursor.fetchone()
    conn.close()
    return friendship is not None


def search_users(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Make search case-insensitive and more flexible
    search_term = f"%{query.lower()}%"
    cursor.execute(
        """SELECT * FROM user 
           WHERE LOWER(first_name) LIKE %s 
           OR LOWER(last_name) LIKE %s 
           OR LOWER(email) LIKE %s
           OR LOWER(CONCAT(first_name, ' ', last_name)) LIKE %s
           ORDER BY first_name, last_name""",
        (search_term, search_term, search_term, search_term)
    )
    users = cursor.fetchall()
    print(f"DEBUG search_users: Query='{query}', Found {len(users)} users")
    conn.close()
    return users


def get_all_users():
    """Get all users from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user ORDER BY first_name, last_name")
    users = cursor.fetchall()
    conn.close()
    return users


def search_posts(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM post 
           WHERE title LIKE %s OR content LIKE %s
           ORDER BY date DESC""",
        (f"%{query}%", f"%{query}%")
    )
    posts = cursor.fetchall()
    conn.close()
    return posts


def delete_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post WHERE id=%s", (post_id,))
    conn.commit()
    conn.close()


def get_post_likes(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM `like` WHERE post_id=%s", (post_id,))
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_post_dislikes(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM dislike WHERE post_id=%s", (post_id,))
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def get_post_comments_count(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM comment WHERE post_id=%s", (post_id,))
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0


def user_liked_post(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `like` WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def user_disliked_post(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dislike WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def remove_like(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `like` WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    conn.commit()
    conn.close()


def remove_dislike(user_id, post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dislike WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    conn.commit()
    conn.close()


def get_all_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE drafts = FALSE ORDER BY date DESC")
    posts = cursor.fetchall()
    print(f"DEBUG get_all_posts: Retrieved {len(posts)} posts from database")
    for post in posts:
        print(f"DEBUG get_all_posts: Post ID {post['id']}: {post['title']}")
    conn.close()
    return posts
