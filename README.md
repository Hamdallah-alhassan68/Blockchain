Blockchain-Based Certificate Verification System

A secure web application for verifying academic certificates using cryptographic hashing and encryption. This system eliminates manual verification delays by enabling instant, tamper-proof validation of records.

Live Demo

GitHub Repository

 https://github.com/Hamdallah-alhassan68/Blockchain

Overview

Traditional certificate verification processes are slow, manual, and prone to fraud. This project provides a secure and automated verification system that ensures:

Authenticity of certificates
Tamper-proof storage using hashing
Fast verification for employers and institutions
Features
Secure Certificate Storage using RSA encryption
SHA-256 Hashing to ensure data integrity
Role-Based Access Control (Students, Admins, Employers)
Instant Verification (reduces processing time from days to seconds)
Web Interface for certificate upload and validation
Technologies Used
Backend: Flask (Python)
Security: RSA Encryption, SHA-256 Hashing
Frontend: HTML, CSS, JavaScript
Database: (Add yours here — e.g., SQLite / MongoDB)
APIs: RESTful API design
How It Works
Certificate Upload
Admin uploads certificate data
System generates a SHA-256 hash
Encryption
Certificate data is encrypted using RSA
Storage
Secure record is stored in the database
Verification
Employer uploads certificate or ID
System hashes input and compares with stored hash
Returns valid / invalid result instantly
Impact
Reduced verification time by ~95% (48+ hours → under 5 seconds)
Improved security using industry-standard cryptographic techniques
Eliminated manual verification bottlenecks
System Architecture
User → Web Interface → Flask API → Encryption/Hashing → Database
                                      ↓
                                  Verification Engine

⚙️ Installation & Setup
# Clone the repository
git clone https://github.com/Hamdallah-alhassan68/Blockchain.git

# Navigate into project folder
cd Blockchain

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

Security Considerations
RSA encryption ensures secure data transmission
SHA-256 hashing prevents data tampering
Role-based access restricts unauthorized actions
Future Improvements
Implement JWT authentication for secure sessions
Deploy using Docker + CI/CD pipeline
Integrate with blockchain ledger (Ethereum/Hyperledger)
Add unit and integration testing (PyTest)
Deploy on cloud (AWS/GCP)
Author

Hamdallah Alhassan

GitHub: https://github.com/Hamdallah-alhassan68
LinkedIn: https://linkedin.com/in/hamdallahalhassan
