# Social Media Application

A full-featured social media application built with Flask, MySQL, and Bootstrap. Users can create accounts, post content with images, interact with posts through likes/dislikes, comment on posts, and manage friendships.

## Features

### 🔐 Authentication & User Management
- User registration and login
- Secure password hashing with Werkzeug
- Profile management with bio and profile pictures
- Password change functionality

### 📝 Posts & Content
- Create posts with text content
- Upload and display images with posts
- Categorize posts (General, Technology, Lifestyle, Travel, Food)
- Tag posts with custom tags
- Save posts as drafts
- Delete your own posts

### 💬 Social Interactions
- Like and dislike posts
- Comment on posts
- View post details with all comments
- Real-time interaction counts

### 👥 Friend System
- Send friend requests to other users
- Accept or reject friend requests
- View friends list
- Search for users and posts

### 🔍 Search & Discovery
- Search for posts by title or content
- Search for users by name or email
- Browse all public posts on home feed

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: MySQL with PyMySQL connector
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **File Uploads**: Werkzeug secure filename handling
- **Security**: Password hashing, CSRF protection

## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd social-media-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Start your MySQL server
2. Create a database named `socialmedia_application`
3. Update database credentials in `website/__init__.py` if needed:
   ```python
   DB_USER = "root"
   DB_PASSWORD = ""  # Your MySQL password
   DB_HOST = "localhost"
   DB_NAME = "socialmedia_application"
   ```

### 4. Run the Application
```bash
python main.py
```

The application will:
- Automatically create all necessary database tables
- Start the Flask development server
- Be accessible at `http://localhost:5000`

## Project Structure

```
social-media-app/
├── website/
│   ├── __init__.py          # App factory and database setup
│   ├── auth.py              # Authentication routes
│   ├── views.py             # Main application routes
│   ├── models.py            # Database operations
│   ├── static/
│   │   ├── style.css        # Custom CSS styles
│   │   ├── fade_in.css      # Animation styles
│   │   ├── uploads/         # User uploaded images
│   │   └── profile_pictures/ # User profile pictures
│   └── templates/
│       ├── base.html        # Base template
│       ├── home.html        # Home feed
│       ├── login_page.html  # Login form
│       ├── signup_page.html # Registration form
│       ├── create_post.html # Post creation form
│       ├── profile.html     # User profiles
│       ├── edit_user_profile.html # Profile editing
│       ├── post_detail.html # Individual post view
│       ├── search.html      # Search results
│       ├── friends.html     # Friends list
│       └── friend_requests.html # Friend requests
├── instance/
│   └── database.db          # SQLite database (if used)
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── test_app.py             # Application tests
└── README.md               # This file
```

## Database Schema

The application uses the following MySQL tables:

- **user**: User accounts and profiles
- **post**: User posts with content and metadata
- **like/dislike**: Post reactions
- **comment**: Post comments
- **reply_comment**: Replies to comments
- **comment_like**: Comment reactions
- **friend_request**: Friend request management
- **friendship**: Established friendships

## Usage

### Getting Started
1. Visit `http://localhost:5000`
2. Create a new account or login with existing credentials
3. Complete your profile setup

### Creating Posts
1. Click "Create Post" in the navigation
2. Add title, content, and optional image
3. Select category and add tags
4. Choose to publish or save as draft

### Social Features
1. **Like/Dislike**: Click thumbs up/down on any post
2. **Comment**: Use the comment box below posts
3. **Friend Requests**: Search for users and send friend requests
4. **Profile**: View and edit your profile information

## Testing

Run the included test script to verify everything is working:

```bash
python test_app.py
```

This will test:
- Application creation
- Database connectivity
- Route accessibility

## Security Features

- Password hashing using PBKDF2 with SHA256
- Secure file upload handling
- SQL injection prevention with parameterized queries
- CSRF protection with Flask's built-in security
- User authentication required for protected routes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:
1. Check that MySQL is running
2. Verify database credentials
3. Ensure all dependencies are installed
4. Run the test script to identify problems

For additional help, please create an issue in the repository.
