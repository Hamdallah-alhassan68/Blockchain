from flask import Flask, render_template, request
from blockchain import Blockchain
import sqlite3
from flask import render_template
from flask import session, redirect, url_for
from flask import send_file
from io import BytesIO
import hashlib
from flask import jsonify
import os
from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas





# Only generate/load once
if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)
else:
    with open("key.key", "rb") as f:
        key = f.read()

cipher = Fernet(key)  # Use this cipher everywhere




def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create certificates table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        course TEXT,
        grade TEXT,
        cert_hash TEXT,
        encrypted_data TEXT
    )
    ''')

    # Create users table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')

    conn.commit()
    conn.close()


def add_default_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()



    # Hash passwords
    admin_pass = hashlib.sha256("1234".encode()).hexdigest()
    employer_pass = hashlib.sha256("1234".encode()).hexdigest()

    student_pass = hashlib.sha256("1234".encode()).hexdigest()

    users = [
        ('admin', admin_pass, 'university'),
        ('employer', employer_pass, 'employer'),
        ('student1', student_pass, 'student')  # student user
    ]

    for username, password, role in users:
        # Check if user exists already
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )

    conn.commit()
    conn.close()


app = Flask(__name__)
blockchain = Blockchain()


# Encrypt and store safely
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    try:
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return cipher.decrypt(encrypted_data).decode()
    except Exception:
        return "ERROR: Decryption failed"



# 🏫 ISSUE CERTIFICATE

@app.route('/add_certificate', methods=['POST'])
def add_certificate():
    data = request.get_json()


    name = data['student_name']
    course = data['course']
    grade = data['grade']

    # Create hash
    raw_data = f"{name}{course}{grade}"
    cert_hash = hashlib.sha256(raw_data.encode()).hexdigest()

    # Encrypt
    encrypted = encrypt_data(raw_data)

    # Save to DB
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    INSERT INTO certificates (student_name, course, grade, cert_hash, encrypted_data)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, course, grade, cert_hash, encrypted))

    conn.commit()
    conn.close()

    # Add to pending blockchain (NOT mined yet)
    blockchain.add_certificate(cert_hash)

    return {
        "message": "Certificate added (pending mining)",
        "certificate_id": cert_hash
    }
@app.route('/mine_block', methods=['GET'])
def mine_block():
    block = blockchain.mine_block()

    return {
        "message": "Block mined successfully",
        "block": block
    }
@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    data = request.get_json()
    cert_hash = data['certificate_id']

    # Blockchain check
    if not blockchain.is_valid(cert_hash):
        return jsonify({"status": "invalid", "message": "Not found in blockchain"})

    # DB check
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM certificates WHERE cert_hash=?", (cert_hash,))
    result = c.fetchone()
    conn.close()

    if result:
        decrypted = decrypt_data(result[5])  # this now works
        return jsonify({"status": "valid", "data": decrypted})

    return jsonify({"status": "invalid", "message": "Not found"})

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    if 'role' not in session or session['role'] != 'university':
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        grade = request.form['grade']

        # Create hash (Certificate ID)
        data = f"{name}{course}{grade}"
        cert_hash = hashlib.sha256(data.encode()).hexdigest()

        # Encrypt data
        encrypted = encrypt_data(data)

        # Store in DB
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('''
        INSERT INTO certificates (student_name, course, grade, cert_hash, encrypted_data)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, course, grade, cert_hash, encrypted))

        conn.commit()
        conn.close()

        # Add to blockchain
        blockchain.add_data(cert_hash)

        return f"""
        <h3>Certificate Issued</h3>
        <p>Student: {name}</p>
        <p>Certificate ID (Give to Student):</p>
        <b>{cert_hash}</b>
        """

    return render_template('university.html')


# 🏢 VERIFY CERTIFICATE
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        cert_hash = request.form['hash']

        # Check blockchain
        if not blockchain.is_valid(cert_hash):
            return "❌ Certificate NOT FOUND on blockchain"

        # Check DB
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM certificates WHERE cert_hash=?", (cert_hash,))
        result = c.fetchone()
        conn.close()

        if result:
            encrypted_data = result[5]
            decrypted = decrypt_data(encrypted_data)

            return f"""
            ✅ VALID CERTIFICATE<br><br>
            Decrypted Data:<br>
            {decrypted}
            """
        else:
            return "❌ Certificate NOT FOUND in database"

    return render_template('employer.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            session['role'] = user[3]

            if user[3] == 'university':
                return redirect('/university')
            elif user[3] == 'employer':
                return redirect('/employer')
            elif user[3] == 'student':
                return redirect('/student_dashboard')
        return "❌ Invalid login"
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    name = request.args.get('name')
    if not name:
        return redirect('/student')  # redirect to login if no name

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT cert_hash, course, grade, encrypted_data FROM certificates WHERE student_name=?", (name,))
    certificates = c.fetchall()
    conn.close()

    decrypted_certs = []
    for cert in certificates:
        cert_hash, course, grade, encrypted = cert
        decrypted_data = decrypt_data(encrypted)
        decrypted_certs.append({
            "cert_hash": cert_hash,
            "course": course,
            "grade": grade,
            "data": decrypted_data
        })

    return render_template('student_dashboard.html', username=name, certificates=decrypted_certs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/university')
def university():
    return render_template('university.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/employer')
def employer():
    return render_template('employer.html')

@app.route('/get_certificate_id', methods=['POST'])
def get_certificate_id():
    data = request.get_json()
    name = data['student_name']
    course = data['course']
    grade = data['grade']
    raw_data = f"{name}{course}{grade}"
    cert_hash = hashlib.sha256(raw_data.encode()).hexdigest()
    return {"certificate_id": cert_hash}
@app.route('/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    name = data['name'].strip()
    password = data['password'].strip()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT course, grade FROM certificates WHERE student_name=?", (name,))
    certs = c.fetchall()
    conn.close()

    if not certs:
        print("No certificates found for:", name)
        return {"status": "fail"}

    for course, grade in certs:
        course = course.strip()
        grade = grade.strip()

        expected_password = f"{course}{grade}"

        print("Expected:", expected_password)
        print("Entered :", password)

        if password == expected_password:
            print("LOGIN SUCCESS")
            session['username'] = name
            session['role'] = 'student'
            return {"status": "success"}

    print("LOGIN FAILED")
    return {"status": "fail"}


@app.route('/view_db')
def view_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM certificates")
    data = c.fetchall()
    conn.close()

    return str(data)


@app.route('/download_certificate/<cert_hash>')
def download_certificate(cert_hash):
    if 'username' not in session:
        return redirect('/login')

    username = session['username']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT student_name, course, grade, encrypted_data FROM certificates WHERE cert_hash=? AND student_name=?", 
              (cert_hash, username))
    cert = c.fetchone()
    conn.close()

    if not cert:
        return "❌ Certificate not found"

    student_name, course, grade, encrypted_data = cert
    decrypted_data = decrypt_data(encrypted_data)

    # Create PDF in memory
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle("Certificate")
    
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(300, 750, "🎓 Academic Certificate")
    
    pdf.setFont("Helvetica", 14)
    pdf.drawString(50, 700, f"Student Name: {student_name}")
    pdf.drawString(50, 680, f"Course: {course}")
    pdf.drawString(50, 660, f"Grade: {grade}")
    pdf.drawString(50, 640, f"Certificate Hash: {cert_hash}")
    pdf.drawString(50, 620, f"Decrypted Data: {decrypted_data}")

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=f"{student_name}_certificate.pdf", mimetype='application/pdf')


app.secret_key = "secret123"

if __name__ == "__main__":
    init_db()
    add_default_users()
    app.run(debug=True)
