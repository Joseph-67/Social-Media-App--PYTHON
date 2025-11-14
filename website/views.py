from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from .models import (
    get_user_by_id, get_user_posts, create_post, create_post_with_image,
    get_post_by_id, get_post_comments,
    add_comment, reply_to_comment,
    like_post, dislike_post, like_comment,
    get_post_likes, get_post_dislikes, get_post_comments_count,
    user_liked_post, user_disliked_post, remove_like, remove_dislike,
    get_all_posts, update_user
)

views = Blueprint('views', __name__)

# Month mapping for user join dates
months = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


# ---------------- HOME PAGE ----------------
@views.route("/home/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        search_term = request.form.get("search", "").strip()
        if search_term:
            return redirect(url_for("views.search", search=search_term))
        else:
            flash("Please enter a search term.", category="error")

    posts = []
    # Get all posts, not just current user's posts
    all_posts = get_all_posts()
    print(f"DEBUG HOME: Found {len(all_posts)} posts in database")
    
    for p in all_posts:
        print(f"DEBUG HOME: Processing post ID {p['id']}: {p['title']}")
        user = get_user_by_id(p['user_id'])
        if user:  # Only add posts where user exists
            # Add like/dislike/comment data
            p['likes_count'] = get_post_likes(p['id'])
            p['dislikes_count'] = get_post_dislikes(p['id'])
            p['comments_count'] = get_post_comments_count(p['id'])
            p['user_liked'] = user_liked_post(current_user.id, p['id'])
            p['user_disliked'] = user_disliked_post(current_user.id, p['id'])
            posts.append({'post': p, 'user': user})
        else:
            print(f"DEBUG HOME: Skipping post {p['id']} - user not found")

    response = render_template("home.html", user=current_user, page="Home", posts=posts)
    # Add cache control headers to prevent caching
    from flask import make_response
    response = make_response(response)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response




# ---------------- PROFILE ----------------
@views.route("/profile/")
@login_required
def profile_redirect():
    return redirect(url_for("views.user_profile", id=current_user.id))


@views.route("/profile/<int:id>")
@login_required
def user_profile(id):
    from .models import are_friends, get_pending_friend_requests, get_sent_friend_requests
    
    user = get_user_by_id(id)
    if not user:
        flash("User not found.", category="error")
        return redirect(url_for("views.home"))

    posts_raw = get_user_posts(id)[:5]
    posts = [{'post': p, 'user': user} for p in posts_raw]

    name = f"{user['first_name']} {user['last_name']}"
    pagename = f"{name}'s Profile"

    # Format date joined
    date_joined = str(user['date_joined']).split(" ")[0]
    y, m, d = date_joined.split("-")
    month = months.get(int(m))
    formatted_date = f"{month} {d}, {y}"

    # Check friendship status
    is_friend = are_friends(current_user.id, id) if id != current_user.id else False
    
    # Check if there's a pending request
    pending_requests = get_pending_friend_requests(current_user.id)
    sent_requests = get_sent_friend_requests(current_user.id)
    
    has_pending_request = any(req['sender_id'] == id for req in pending_requests)
    has_sent_request = any(req['receiver_id'] == id for req in sent_requests)

    return render_template(
        "profile.html",
        page=pagename,
        profile_user=user,
        user=current_user,
        id=id,
        date_joined=formatted_date,
        posts=posts,
        is_friend=is_friend,
        has_pending_request=has_pending_request,
        has_sent_request=has_sent_request
    )


# ---------------- EDIT PROFILE ----------------
@views.route("/edit/profile/")
@login_required
def redirect_to_edit_profile():
    return redirect(f"/edit/profile/{current_user.id}")


@views.route("/edit/profile/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    if id != current_user.id:
        flash("You can only edit your own profile.", category="error")
        return redirect(url_for("views.home"))
    
    if request.method == "POST":
        from werkzeug.security import check_password_hash, generate_password_hash
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        old_password = request.form.get("old_password")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        bio = request.form.get("bio")
        
        # Get current user data
        user_data = get_user_by_id(current_user.id)
        
        # Prepare fields to update
        fields_to_update = {}
        
        # Update basic info
        if first_name and first_name != user_data['first_name']:
            fields_to_update['first_name'] = first_name
        if last_name and last_name != user_data['last_name']:
            fields_to_update['last_name'] = last_name
        if email and email != user_data['email']:
            fields_to_update['email'] = email
        if bio is not None:
            fields_to_update['bio'] = bio
        
        # Handle password change
        if old_password and password1 and password2:
            if not check_password_hash(user_data['password'], old_password):
                flash("Current password is incorrect.", category="error")
                return render_template("edit_user_profile.html", user=current_user, current_user=user_data)
            elif password1 != password2:
                flash("New passwords don't match.", category="error")
                return render_template("edit_user_profile.html", user=current_user, current_user=user_data)
            elif len(password1) < 7:
                flash("New password must be at least 7 characters.", category="error")
                return render_template("edit_user_profile.html", user=current_user, current_user=user_data)
            else:
                fields_to_update['password'] = generate_password_hash(password1, method="pbkdf2:sha256")
        
        # Update the database
        if fields_to_update:
            update_user(current_user.id, fields_to_update)
            flash("Profile updated successfully!", category="success")
            return redirect(url_for("views.user_profile", id=current_user.id))
        else:
            flash("No changes were made.", category="info")
    
    user_data = get_user_by_id(current_user.id)
    return render_template("edit_user_profile.html", user=current_user, current_user=user_data)


@views.route("/edit/profile/<int:id>/profile_picture", methods=['GET', 'POST'])
@login_required
def edit_profile_picture(id):
    if id != current_user.id:
        flash("You can only edit your own profile picture.", category="error")
        return redirect(url_for("views.home"))
    
    if request.method == "POST":
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                import os
                
                # Check if file is allowed
                def allowed_file(filename):
                    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
                    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
                
                if allowed_file(file.filename):
                    # Create profile pictures directory if it doesn't exist
                    upload_folder = os.path.join('website', 'static', 'profile_pictures')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Save the file
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid conflicts
                    import time
                    timestamp = str(int(time.time()))
                    name, ext = os.path.splitext(filename)
                    profile_picture_filename = f"{name}_{timestamp}{ext}"
                    
                    file_path = os.path.join(upload_folder, profile_picture_filename)
                    file.save(file_path)
                    
                    # Update user's profile picture in database
                    update_user(current_user.id, {'profile_picture': profile_picture_filename})
                    flash('Profile picture updated successfully!', category='success')
                    return redirect(url_for('views.user_profile', id=current_user.id))
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', category='error')
            else:
                flash('No file selected.', category='error')
    
    return render_template("edit_user_profile_picture.html", user=current_user)


@views.route("/edit/profile/<int:id>/remove_profile_picture/")
@login_required
def remove_profile_picture(id):
    if id != current_user.id:
        flash("You can only edit your own profile picture.", category="error")
        return redirect(url_for("views.home"))
    
    # Reset to default profile picture
    update_user(current_user.id, {'profile_picture': 'default_profile_photo.jpg'})
    flash('Profile picture removed successfully!', category='success')
    return redirect(url_for('views.edit_profile_picture', id=current_user.id))


# create post
@views.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post_route():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        tags = request.form.get('tags')
        is_draft = request.form.get('draft') is not None
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            print(f"DEBUG: File received: {file.filename}")
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                import os
                
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join('website', 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                print(f"DEBUG: Upload folder: {upload_folder}")
                
                # Save the file
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                image_filename = f"{name}_{timestamp}{ext}"
                
                file_path = os.path.join(upload_folder, image_filename)
                print(f"DEBUG: Saving file to: {file_path}")
                file.save(file_path)
                
                # Check if file was saved
                if os.path.exists(file_path):
                    print(f"DEBUG: File saved successfully: {image_filename}")
                else:
                    print(f"DEBUG: File NOT saved!")
            else:
                print("DEBUG: No file or empty filename")
        
        if not content:
            flash('Post content cannot be empty', category='error')
        else:
            # Debug: Print what we're trying to save
            print(f"DEBUG: Saving post with image: {image_filename}")
            print(f"DEBUG: Title: {title}, Content: {content[:50]}...")
            
            create_post_with_image(title, content, current_user.id, image_filename, category, tags, is_draft)
            flash('Post created successfully!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('create_post.html', user=current_user)


# Debug route to check posts
@views.route('/debug/posts')
@login_required
def debug_posts():
    posts = get_all_posts()
    output = f"<h2>All Posts Debug ({len(posts)} posts found)</h2>"
    output += "<a href='/home/'>← Back to Home</a><br><br>"
    
    if not posts:
        output += "<p><strong>No posts found in database!</strong></p>"
    else:
        for post in posts:
            output += f"<div style='border: 1px solid #ccc; padding: 10px; margin: 10px 0;'>"
            output += f"<strong>ID:</strong> {post['id']}<br>"
            output += f"<strong>Title:</strong> {post['title']}<br>"
            output += f"<strong>Content:</strong> {post['content'][:100]}...<br>"
            output += f"<strong>Image:</strong> {post['image']}<br>"
            output += f"<strong>User ID:</strong> {post['user_id']}<br>"
            output += f"<strong>Date:</strong> {post['date']}<br>"
            output += f"<strong>Drafts:</strong> {post['drafts']}<br>"
            output += "</div>"
    return output


# Route to force refresh database connection
@views.route('/debug/refresh')
@login_required
def debug_refresh():
    # Force a fresh database connection
    from . import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM post")
    result = cursor.fetchone()
    conn.close()
    
    return f"<h2>Database Refresh</h2><p>Total posts in database: {result['count']}</p><a href='/home/'>← Back to Home</a>"
# ---------------- DELETE POST ----------------
@views.route("/delete/post/<int:id>")
@login_required
def delete_post(id):
    from .models import delete_post as delete_post_db
    post = get_post_by_id(id)

    if not post or int(post['user_id']) != int(current_user.id):
        flash("You can only delete your own posts.", category="error")
        return redirect(url_for("views.home"))

    delete_post_db(id)
    flash("Post deleted successfully.", category="success")
    return redirect(url_for("views.profile_redirect"))

# ---------------- SEARCH ----------------
@views.route("/search", methods=["GET", "POST"])
@views.route("/search/<search>")
@login_required
def search(search=None):
    from .models import search_posts, search_users

    if request.method == "POST":
        search = request.form.get("search", "").strip()
        if search:
            return redirect(url_for("views.search", search=search))
        else:
            flash("Please enter a search term.", category="error")
            return redirect(url_for("views.home"))

    if not search:
        return render_template(
            'search.html',
            posts=[],
            users=[],
            query="",
            user=current_user,
            page="Search"
        )

    posts_raw = search_posts(search)
    posts = []
    for p in posts_raw:
        user = get_user_by_id(p['user_id'])
        posts.append((p, user))

    users = search_users(search) if len(search) > 1 else []
    
    # Debug: Print search results
    print(f"DEBUG SEARCH: Query='{search}', Found {len(users)} users, {len(posts)} posts")

    return render_template(
        'search.html',
        posts=posts,
        users=users,
        query=search,
        user=current_user,
        page="Search"
    )


# ---------------- FIND PEOPLE ----------------
@views.route("/find_people")
@login_required
def find_people():
    from .models import get_all_users, are_friends, get_pending_friend_requests, get_sent_friend_requests
    
    # Get all users except current user
    all_users = get_all_users()
    users = [u for u in all_users if u['id'] != current_user.id]
    
    # Get friend request info
    pending_requests = get_pending_friend_requests(current_user.id)
    sent_requests = get_sent_friend_requests(current_user.id)
    
    # Add friendship status to each user
    for user in users:
        user['is_friend'] = are_friends(current_user.id, user['id'])
        user['has_pending_request'] = any(req['sender_id'] == user['id'] for req in pending_requests)
        user['has_sent_request'] = any(req['receiver_id'] == user['id'] for req in sent_requests)
    
    return render_template(
        'find_people.html',
        users=users,
        user=current_user,
        page="Find People"
    )


# ---------------- POST REACTIONS ----------------
@views.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post_route(post_id):
    # Check if user already liked the post
    if user_liked_post(current_user.id, post_id):
        # Remove like
        remove_like(current_user.id, post_id)
    else:
        # Remove dislike if exists, then add like
        if user_disliked_post(current_user.id, post_id):
            remove_dislike(current_user.id, post_id)
        like_post(current_user.id, post_id)
    
    return redirect(request.referrer or url_for('views.home'))


@views.route("/post/<int:post_id>/dislike", methods=["POST"])
@login_required
def dislike_post_route(post_id):
    # Check if user already disliked the post
    if user_disliked_post(current_user.id, post_id):
        # Remove dislike
        remove_dislike(current_user.id, post_id)
    else:
        # Remove like if exists, then add dislike
        if user_liked_post(current_user.id, post_id):
            remove_like(current_user.id, post_id)
        dislike_post(current_user.id, post_id)
    
    return redirect(request.referrer or url_for('views.home'))


# ---------------- POST DETAIL ----------------
@views.route("/post/<int:id>")
@login_required
def view_post(id):
    post = get_post_by_id(id)
    if not post:
        flash("Post not found.", category="error")
        return redirect(url_for("views.home"))
    
    user = get_user_by_id(post['user_id'])
    comments = get_post_comments(id)
    
    # Add user info to each comment
    for comment in comments:
        comment['user'] = get_user_by_id(comment['user_id'])
    
    # Add like/dislike/comment data
    post['likes_count'] = get_post_likes(post['id'])
    post['dislikes_count'] = get_post_dislikes(post['id'])
    post['comments_count'] = get_post_comments_count(post['id'])
    post['user_liked'] = user_liked_post(current_user.id, post['id'])
    post['user_disliked'] = user_disliked_post(current_user.id, post['id'])
    
    return render_template("post_detail.html", post=post, user=current_user, post_user=user, comments=comments, page="Post")


# ---------------- COMMENTS ----------------
@views.route("/post/<int:id>/comment/", methods=["POST"])
@login_required
def comment_on_post(id):
    comment_data = request.form.get("comment")
    if comment_data and comment_data.strip():
        add_comment(current_user.id, id, comment_data.strip())
        flash("Comment added.", category="success")
    else:
        flash("Comment cannot be empty.", category="error")
    return redirect(request.referrer or url_for('views.view_post', id=id))


@views.route("/comment/<int:id>/reply/", methods=["POST"])
@login_required
def reply_to_comment_route(id):
    reply_data = request.form.get("reply")
    if reply_data and reply_data.strip():
        reply_to_comment(current_user.id, id, None, reply_data.strip())
        flash("Reply added.", category='success')
    else:
        flash("Reply cannot be empty.", category='error')
    return redirect(request.referrer or url_for('views.home'))


# ---------------- FRIEND REQUESTS ----------------
@views.route("/send_friend_request/<int:user_id>", methods=["POST"])
@login_required
def send_friend_request_route(user_id):
    from .models import send_friend_request, are_friends
    
    if user_id == current_user.id:
        flash("You cannot send a friend request to yourself.", category="error")
        return redirect(request.referrer or url_for('views.home'))
    
    if are_friends(current_user.id, user_id):
        flash("You are already friends with this user.", category="info")
        return redirect(request.referrer or url_for('views.home'))
    
    success = send_friend_request(current_user.id, user_id)
    if success:
        flash("Friend request sent successfully!", category="success")
    else:
        flash("Friend request already sent.", category="info")
    
    return redirect(request.referrer or url_for('views.home'))


@views.route("/accept_friend_request/<int:request_id>", methods=["POST"])
@login_required
def accept_friend_request_route(request_id):
    from .models import accept_friend_request
    accept_friend_request(request_id)
    flash("Friend request accepted!", category="success")
    return redirect(url_for('views.friend_requests'))


@views.route("/reject_friend_request/<int:request_id>", methods=["POST"])
@login_required
def reject_friend_request_route(request_id):
    from .models import reject_friend_request
    reject_friend_request(request_id)
    flash("Friend request rejected.", category="info")
    return redirect(url_for('views.friend_requests'))


@views.route("/friend_requests")
@login_required
def friend_requests():
    from .models import get_pending_friend_requests, get_sent_friend_requests
    
    pending_requests = get_pending_friend_requests(current_user.id)
    sent_requests = get_sent_friend_requests(current_user.id)
    
    return render_template(
        "friend_requests.html",
        user=current_user,
        page="Friend Requests",
        pending_requests=pending_requests,
        sent_requests=sent_requests
    )


@views.route("/friends")
@login_required
def friends():
    from .models import get_user_friends
    
    friends = get_user_friends(current_user.id)
    
    return render_template(
        "friends.html",
        user=current_user,
        page="My Friends",
        friends=friends
    )


# ---------------- LOGOUT ----------------
@views.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", category="success")
    return redirect(url_for("auth.login_page"))
