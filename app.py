from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import Config

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config.from_object(Config)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', books=books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        user_id = session.get('user_id')
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO books (title, author, user_id) VALUES (%s, %s, %s)", (title, author, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/my_books')
def my_books():
    user_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE user_id = %s", (user_id,))
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('my_books.html', books=books)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('my_books'))

if __name__ == '__main__':
    app.run(debug=True)
