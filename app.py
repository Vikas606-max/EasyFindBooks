# =========================
# Imports & Configurations
# =========================
from flask import Flask, render_template, request, redirect, session, flash, url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pickle
import numpy as np
import sqlite3
import os
import random
import pandas as pd
from datetime import datetime
import requests


# =========================
# Flask App Setup
# =========================
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/profile_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
GUTENDEX_API = "https://gutendex.com/books/"

# =========================
# Data Loading
# =========================
popular_df = pickle.load(open('C:/Users/admin/OneDrive/Desktop/Project/templates/popular.pkl', 'rb'))
pt = pickle.load(open('C:/Users/admin/OneDrive/Desktop/Project/templates/pt.pkl', 'rb'))
books = pickle.load(open('C:/Users/admin/OneDrive/Desktop/Project/templates/books.pkl', 'rb'))
similarity_scores = pickle.load(open('C:/Users/admin/OneDrive/Desktop/Project/templates/similarity_scores.pkl', 'rb'))

# =========================
# Mood Book Map
# =========================
mood_book_map = {
    'happy': [
        'The Alchemist', 'Harry Potter and the Sorcerer\'s Stone', 'The Secret', 'Eleanor Oliphant Is Completely Fine',
        'Wonder', 'Good Omens', 'The Rosie Project', 'Bossypants', 'Yes Please', 'Where’d You Go, Bernadette',
        'The 100-Year-Old Man Who Climbed Out the Window and Disappeared', 'My Grandmother Asked Me to Tell You She’s Sorry',
        'Oona Out of Order', 'A Man Called Ove', 'Love Your Life'
    ],
    'sad': [
        'The Book Thief', 'Me Before You', 'The Lovely Bones', 'The Kite Runner', 'A Little Life',
        'Extremely Loud & Incredibly Close', 'The Light Between Oceans', 'Bridge to Terabithia', 'The Midnight Library',
        'The Art of Racing in the Rain', 'Room', 'My Sister’s Keeper', 'We Were Liars', 'They Both Die at the End',
        'If I Stay'
    ],
    'motivated': [
        'Atomic Habits', 'Deep Work', 'Grit', 'The Power of Habit', 'Can\'t Hurt Me', 'Make Your Bed',
        'Mindset', 'The 7 Habits of Highly Effective People', 'Think and Grow Rich', 'The Magic of Thinking Big',
        'The War of Art', 'Limitless', 'Drive', 'Start with Why', 'Do the Work'
    ],
    'romantic': [
        'Pride and Prejudice', 'The Notebook', 'The Time Traveler’s Wife', 'Call Me by Your Name', 'Red, White & Royal Blue',
        'Beach Read', 'Outlander', 'People We Meet on Vacation', 'The Kiss Quotient', 'It Ends with Us',
        'One Day', 'The Love Hypothesis', 'The Hating Game', 'Jane Eyre', 'Love and Other Words'
    ],
    'adventure': [
        'The Hobbit', 'Life of Pi', 'The Martian', 'Into the Wild', 'The Call of the Wild',
        'Treasure Island', 'Jurassic Park', 'Around the World in 80 Days', 'The Three Musketeers', 'The Maze Runner',
        'Percy Jackson & the Olympians', 'Ready Player One', 'Hatchet', 'Journey to the Center of the Earth',
        'The Golden Compass'
    ],
    'mystery': [
        'Gone Girl', 'The Girl with the Dragon Tattoo', 'The Da Vinci Code', 'In the Woods', 'The Silent Patient',
        'Big Little Lies', 'Sharp Objects', 'The Woman in White', 'The Girl on the Train', 'Before I Go to Sleep',
        'Behind Closed Doors', 'The Couple Next Door', 'The Family Upstairs', 'And Then There Were None',
        'The Hound of the Baskervilles'
    ],
    'chill': [
        'The Little Prince', 'The Secret Garden', 'Anne of Green Gables', 'The Wind in the Willows', 'Where the Crawdads Sing',
        'Stardust', 'Garden Spells', 'Norwegian Wood', 'Eleanor & Park', 'The House on Mango Street',
        'The Giver of Stars', 'Little Women', 'The Flatshare', 'Evvie Drake Starts Over', 'The Midnight Library'
    ],
    'inspirational': [
        'The Power of Now', 'Man\'s Search for Meaning', 'The Four Agreements', 'Daring Greatly', 'The Untethered Soul',
        'The Art of Happiness', 'You Can Heal Your Life', 'The Monk Who Sold His Ferrari', 'Big Magic', 'Tuesdays with Morrie',
        'The Last Lecture', 'The Gifts of Imperfection', 'The Road Less Traveled', 'Braving the Wilderness',
        'Think Like a Monk'
    ],
    'thriller': [
        'The Silent Patient', 'Shutter Island', 'Before I Go to Sleep', 'Misery', 'Behind Closed Doors',
        'The Girl on the Train', 'The Woman in Cabin 10', 'The Reversal', 'The Chain', 'I Am Watching You',
        'Verity', 'Home Before Dark', 'The Turn of the Key', 'The Girl Beneath the Sea', 'Final Girls'
    ],
    'fantasy': [
        'Harry Potter and the Sorcerer\'s Stone', 'A Game of Thrones', 'The Name of the Wind', 'The Way of Kings', 'Mistborn',
        'Eragon', 'The Lies of Locke Lamora', 'The Priory of the Orange Tree', 'Throne of Glass', 'Six of Crows',
        'The Dark Tower', 'The Wheel of Time', 'An Ember in the Ashes', 'The Night Circus', 'The House in the Cerulean Sea'
    ],
    'sci-fi': [
        'Dune', 'Ender\'s Game', 'The Martian', 'Neuromancer', 'Foundation', 'Snow Crash', 'Hyperion', 'The Left Hand of Darkness',
        'Ready Player One', 'Altered Carbon', 'The Three-Body Problem', 'Project Hail Mary', 'The Power', 'Red Mars',
        'Dark Matter'
    ],
    'historical': [
        'All the Light We Cannot See', 'The Book Thief', 'The Help', 'The Nightingale', 'Memoirs of a Geisha',
        'Wolf Hall', 'The Pillars of the Earth', 'The Tattooist of Auschwitz', 'The Paris Library', 'A Gentleman in Moscow',
        'The Alice Network', 'Beneath a Scarlet Sky', 'The Guernsey Literary and Potato Peel Pie Society',
        'The Other Boleyn Girl', 'A Tale of Two Cities'
    ],
    'self-help': [
        'How to Win Friends and Influence People', 'Think and Grow Rich', 'Atomic Habits', 'You Are a Badass',
        'The Subtle Art of Not Giving a F*ck', 'Awaken the Giant Within', 'The Power of Now', 'The 7 Habits of Highly Effective People',
        'Make Your Bed', 'Mindset', 'Can\'t Hurt Me', 'The Miracle Morning', 'Who Moved My Cheese?', 'Feel the Fear and Do It Anyway',
        'The Confidence Code'
    ]
}

# =========================
# Utility Functions
# =========================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                password TEXT NOT NULL,
                profile_photo TEXT,
                bio TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                detail TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

# =========================
# Blueprints
# =========================
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

# =========================
# Auth Routes
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            session['name'] = username
            return redirect('/')
        else:
            flash('Invalid username or password.', 'danger')
            return redirect('/login')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return redirect('/signup')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_email = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose another.', 'warning')
            conn.close()
            return redirect('/signup')
        if existing_email:
            flash('Email already registered. Please use another.', 'warning')
            conn.close()
            return redirect('/signup')

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)",
            (name, username, email, phone, hashed_password)
        )
        conn.commit()
        conn.close()

        flash('Signup successful! You can now login.', 'success')
        return redirect('/login')

    return render_template('signup.html')

# =========================
# Profile & Upload Routes
# =========================
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your profile.', 'warning')
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, email, phone, profile_photo, bio FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    cursor.execute(
        "SELECT action, detail, timestamp FROM user_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()

    if user:
        user_name, user_username, user_email, user_phone, profile_photo, user_bio = user
    else:
        user_name = user_username = user_email = user_phone = profile_photo = user_bio = None

    return render_template(
        'profile.html',
        user_name=user_name,
        user_username=user_username,
        user_email=user_email,
        user_phone=user_phone,
        user_image=url_for('static', filename=f'profile_photos/{profile_photo}') if profile_photo else None,
        user_bio=user_bio,
        user_history=history
    )

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'user_id' not in session:
        flash('Please log in to upload a profile photo.', 'warning')
        return redirect('/login')
    file = request.files.get('profile_pic')
    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_photo = ? WHERE id = ?", (filename, session['user_id']))
        conn.commit()
        conn.close()
        flash('Profile photo updated!', 'success')
    else:
        flash('Invalid file type.', 'danger')
    return redirect('/profile')

# =========================
# Book Recommendation Routes
# =========================
@app.route('/')
def index():
    mood_top_books = {}
    for mood, books_list in mood_book_map.items():
        mood_top_books[mood] = []
        for book_title in books_list[:5]:
            temp_df = books[books['Book-Title'] == book_title].drop_duplicates('Book-Title')
            if not temp_df.empty:
                mood_top_books[mood].append({
                    'title': temp_df['Book-Title'].values[0],
                    'author': temp_df['Book-Author'].values[0],
                    'image': temp_df['Image-URL-M'].values[0]
                })

    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values),
        mood_top_books=mood_top_books
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    user_id = session.get('user_id')
    if user_input not in pt.index:
        return render_template('recommend.html', error="Book not found. Please try another title.")

    if user_id:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_history (user_id, action, detail) VALUES (?, ?, ?)",
            (user_id, 'search_book', user_input)
        )
        conn.commit()
        conn.close()

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data, user_input=user_input)

# =========================
# Mood Selection & Book Routes
# =========================
@app.route('/select_mood')
def select_mood():
    moods = list(mood_book_map.keys())
    return render_template('select_mood.html', moods=moods)

@app.route('/get_books_from_mood', methods=['POST'])
def get_books_from_mood():
    mood = request.form.get('mood')
    user_id = session.get('user_id')
    books_for_mood = mood_book_map.get(mood.lower(), [])

    if user_id:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_history (user_id, action, detail) VALUES (?, ?, ?)",
            (user_id, 'select_mood', mood)
        )
        conn.commit()
        conn.close()

    if not books_for_mood:
        return render_template('select_book.html', mood=mood, books=[], error="No books available for this mood.")

    selected_books = random.sample(books_for_mood, min(8, len(books_for_mood)))
    recommended_books = []

    for mood_book in selected_books:
        if mood_book in pt.index:
            index = np.where(pt.index == mood_book)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
                if not temp_df.empty:
                    recommended_books.append({
                        'base': mood_book,
                        'title': temp_df['Book-Title'].values[0],
                        'author': temp_df['Book-Author'].values[0],
                        'image': temp_df['Image-URL-M'].values[0]
                    })
        else:
            temp_df = books[books['Book-Title'] == mood_book].drop_duplicates('Book-Title')
            if not temp_df.empty:
                recommended_books.append({
                    'base': mood_book,
                    'title': temp_df['Book-Title'].values[0],
                    'author': temp_df['Book-Author'].values[0],
                    'image': temp_df['Image-URL-M'].values[0]
                })

    return render_template('select_book.html', mood=mood, books=recommended_books)

# =========================
# Contact Route
# =========================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    from datetime import datetime
    year = datetime.now().year
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (username, email, phone, message) VALUES (?, ?, ?, ?)",
            (username, email, phone, message)
        )
        conn.commit()
        conn.close()
        flash('Your message has been sent!', 'success')
        return redirect('/contact')
    return render_template('contact.html', year=year)

# =========================
# Chatbot Route
# =========================
@app.route('/chatbot')
def chatbot():
    from datetime import datetime
    year = datetime.now().year
    return render_template('chatbot.html', year=year)

# =========================
# Download route
# =========================

@app.route('/book')
def book():
    return render_template("books_dashboard.html")

@app.route('/search')
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    response = requests.get(GUTENDEX_API, params={'search': query})
    if response.status_code != 200:
        return jsonify([])

    data = response.json()
    books = []
    for book in data['results']:
        formats = book['formats']
        books.append({
            "title": book['title'],
            "author": book['authors'][0]['name'] if book['authors'] else "Unknown",
            "download_links": {
                "text": formats.get("text/plain; charset=utf-8"),
                "pdf": formats.get("application/pdf"),
                "epub": formats.get("application/epub+zip"),
                "kindle": formats.get("application/x-mobipocket-ebook")
            }
        })

    return jsonify(books)

# =========================
# Main Entry
# =========================
if __name__ == '__main__':
    app.run(debug=True)


# command to run :   C:/Python313/python.exe c:/Users/admin/OneDrive/Desktop/Project/app.py 

