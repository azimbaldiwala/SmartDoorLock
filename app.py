# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'photo_rec'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
from database import init_db
init_db()

def get_db_connection():
    conn = sqlite3.connect('access_control.db')
    conn.row_factory = sqlite3.Row
    return conn


# Load the public and private keys
def load_public_key():
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key

def load_private_key():
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key

# Encrypt and decrypt functions
def encrypt_password(password):
    public_key = load_public_key()
    encrypted_password = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_password

def decrypt_password(encrypted_password):
    private_key = load_private_key()
    decrypted_password = private_key.decrypt(
        encrypted_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_password.decode()

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE adminUsername = ?", (username,))
        admin = cursor.fetchone()
        conn.close()
        print(admin['password'])
        if admin:
            print("admin")
            encrypted_password = admin['password']
            try:
                # Decrypt password
                decrypted_password = decrypt_password(encrypted_password)
                print(decrypt_password)
                # Compare decrypted password with user input
                if password == decrypted_password:
                    session['admin'] = username
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid credentials.', 'danger')
            except Exception as e:
                flash(f"Decryption error: {str(e)}", 'danger')
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

# Admin logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Dashboard route
@app.route('/')
def admin_dashboard():
    if 'admin' not in session:
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('dashboard.html', users=users)



@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'admin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin']
        email_id = request.form['email_id']
        access_start = request.form['access_start'] if 'access_start' in request.form else None
        access_end = request.form['access_end'] if 'access_end' in request.form else None
        is_24_hours = 1 if 'is_24_hours' in request.form else 0
        photo = request.files['photo']

        if photo and username and pin:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            try:
                # Encrypt the PIN
                public_key = load_public_key()
                encrypted_pin = public_key.encrypt(
                    pin.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Add user to the database
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO users (username, pin, email_id, access_start, access_end, is_24_hours) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, encrypted_pin, email_id, access_start, access_end, is_24_hours))
                conn.commit()
                conn.close()
                flash("User added successfully!", "success")
                return redirect(url_for('admin_dashboard'))
            except sqlite3.IntegrityError:
                flash("Username already exists.", "error")
                return redirect(url_for('add_user'))
    return render_template('add_user.html')

# Route to update user access
@app.route('/update_access/<int:uid>', methods=['GET', 'POST'])
def update_access(uid):
    if 'admin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE UID = ?', (uid,)).fetchone()

    if request.method == 'POST':
        access_start = request.form['access_start'] if 'access_start' in request.form else None
        access_end = request.form['access_end'] if 'access_end' in request.form else None
        is_24_hours = 1 if 'is_24_hours' in request.form else 0

        conn.execute('UPDATE users SET access_start = ?, access_end = ?, is_24_hours = ? WHERE UID = ?',
                     (access_start, access_end, is_24_hours, uid))
        conn.commit()
        conn.close()

        flash("User access updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('update_access.html', user=user)

# Route to view unlock history for each user
@app.route('/history/<int:uid>')
def history(uid):
    if 'admin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT username FROM users WHERE UID = ?', (uid,)).fetchone()
    history = conn.execute('SELECT * FROM access_control WHERE UID = ? ORDER BY attempt_date DESC, attempt_time DESC', (uid,)).fetchall()
    conn.close()
    return render_template('history.html', user=user, history=history)

# Route to delete a user
@app.route('/delete_user/<int:uid>', methods=['POST'])
def delete_user(uid):
    if 'admin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM access_control WHERE UID = ?', (uid,))
    conn.execute('DELETE FROM users WHERE UID = ?', (uid,))
    conn.commit()
    conn.close()
    
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# Route to toggle access status
@app.route('/toggle_access/<int:uid>', methods=['POST'])
def toggle_access(uid):
    if 'admin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT is_access_granted FROM users WHERE UID = ?', (uid,)).fetchone()

    if user:
        new_status = 0 if user['is_access_granted'] == 1 else 1
        conn.execute('UPDATE users SET is_access_granted = ? WHERE UID = ?', (new_status, uid))
        conn.commit()
        conn.close()

        action = "Granted" if new_status == 1 else "Revoked"
        flash(f"Access {action} successfully!", "success")
    else:
        flash("User not found.", "error")

    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
