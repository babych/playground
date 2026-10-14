# Flask log - testing web app using flask and py

Flask project which uses HTML views.

## Functionality

### Authentification 
- Reistration
- Login/logout
- Routing security (login_required)
- Pwd hashing

### CRUD
- **Create** - New posts
- **Read** - Rad all or separate posts
- **Update** - Edit/update
- **Delete** - Delete

### Additional functionality
- User profiles
- User - post relationship
- Flash-messages for users
- Responsive design (Bootstrap 5)
- Form validation

## Project struture

```
/
│
├── app.py                 # main file
├── requirements.txt       # dependencies
├── blog.db               # SQLite db file created locally 
│
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Main page
    ├── register.html     # Registration
    ├── login.html        # Entry
    ├── new_post.html     # Post creation
    ├── view_post.html    # Post view
    ├── edit_post.html    # Post edit
    └── profile.html      # User profile
```

## How to run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run app

```bash
python app.py
```

### 3. Open web browser

Open http://127.0.0.1:5000/

Deployed version into renderer: https://flaskportalpy.onrender.com/

## Tech stack

- **Flask** - web framework
- **Flask-SQLAlchemy** - ORM
- **SQLite** - BD
- **Werkzeug** - pwd hashing
- **Bootstrap 5** - CSS framework
- **Jinja2** - templates (build in into Flask)

## Main Flask conceptions

### 1. Routing
```python
@app.route('/')
def index():
    return render_template('index.html')
```

### 2. HTTP Methods
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Form handling
```

### 3. DB models
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
```

### 4. Sessions
```python
session['user_id'] = user.id
if 'user_id' in session:
    # User logged in
```

### 5. Decorators
```python
@login_required
def protected_route():
    # Only when logged in
```

### 6. Flash messages
```python
flash('Successful action!', 'success')
```

### 7. Templates and inheritance
```python
{% extends "base.html" %}
{% block content %}
    <!-- Content -->
{% endblock %}
```

## Possible improvements

- Paggination
- Comments
- Likes
- Search
- Tags
- Images
- Email verification
- PWD reset
- REST API
- Tests

## Security

1. Edit SECRET_KEY
2. Use PostgreSQL аorбо MySQL instead of SQLite
3. Add HTTPS
4. Make rate limiting
5. Add CSRF protection (Flask-WTF)
6. Server validation
7. Escaped output in templates (Jinja2 does it out of the box)
