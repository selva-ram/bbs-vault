# BBS Vault — Secure OTP Authentication System

A secure OTP authentication system built using Flask and the Blum Blum Shub (BBS) Cryptographically Secure Pseudo-Random Number Generator (CSPRNG).

This project demonstrates the implementation of secure OTP generation and verification with modern backend security practices including rate limiting, constant-time comparison, secure headers, OTP expiry handling, and input validation.

---

##  Features

- Secure OTP generation using Blum Blum Shub (BBS)
- SHA-256 based seed generation
- OTP verification system
- OTP expiry timer
- Rate limiting protection
- Constant-time OTP comparison
- Attempt lockout protection
- Secure Flask backend APIs
- Modern cyber-themed responsive UI
- Real-time audit/system logs
- Entropy stream visualization
- Security headers implementation
- Input validation and sanitization

---

##  Security Concepts Used

### Blum Blum Shub (BBS) CSPRNG
The OTP generation uses the Blum Blum Shub algorithm for cryptographically secure random number generation.

Formula:

x(n+1) = x(n)^2 mod M

Where:
- M = p × q
- p and q are Blum primes

---

##  Security Features

### Backend Security
- Restricted CORS configuration
- Constant-time string comparison
- Rate limiting
- Secure OTP expiry
- Maximum attempt lockout
- Security headers
- Input validation
- Secure hashing with SHA-256

### HTTP Security Headers
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Cache-Control

---

##  Tech Stack

### Backend
- Python
- Flask
- Flask-CORS

### Frontend
- HTML5
- CSS3
- JavaScript

### Security / Cryptography
- Blum Blum Shub (BBS)
- SHA-256
- HMAC constant-time comparison

---

##  Project Structure

```bash
bbs-vault/
│
├── app.py
├── bbs.py
├── config.py
├── otp_service.py
├── requirements.txt
│
├── frontend/
│   ├── index.html
│   └── style.css
│
└── README.md
```

---

##  Installation

### Clone Repository

```bash
git clone https://github.com/selva-ram/bbs-vault.git
```

### Navigate to Project Folder

```bash
cd bbs-vault
```

### Create Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Run the Application

```bash
python app.py
```

Server runs at:

```bash
http://127.0.0.1:5000
```

---

##  Application Features

### OTP Generation
- User ID validation
- Secure OTP generation
- Rate limiting

### OTP Verification
- 6-digit OTP verification
- Expiry timer
- Attempt lockout

### Dashboard UI
- Cyberpunk themed interface
- Entropy visualization
- Audit logs
- Circular OTP timer

---

##  Core Functionalities

### OTP Security
- OTP never returned in API response
- OTP delivered through secure channel
- Auto expiry after 120 seconds
- Max 3 failed attempts

### BBS Generator
- Uses Blum primes
- Cryptographically secure randomness
- Secure modulus generation

---

##  API Endpoints

### Generate OTP

```http
POST /generate-otp
```

#### Request
```json
{
  "user_id": "selvaram"
}
```

---

### Verify OTP

```http
POST /verify-otp
```

#### Request
```json
{
  "user_id": "selvaram",
  "otp": "123456"
}
```

---

##  Requirements

```txt
flask>=3.0.0
flask-cors>=4.0.0
```

---

##  Future Improvements

- Database integration
- Email/SMS OTP delivery
- JWT authentication
- Multi-factor authentication
- Docker deployment
- Redis OTP storage
- HTTPS deployment
- Admin monitoring dashboard

---

##  Author

### Selvaram MS

BE Computer Science Engineering  
Sathyabama Institute of Science and Technology

LinkedIn:
https://www.linkedin.com/in/selvaram-m-s-a93b4b291/

GitHub:
https://github.com/selva-ram

---

##  License

This project is licensed under the MIT License.

---

##  Support

If you like this project:

- Star this repository
- Fork this repository
- Share it on LinkedIn

---

##  Keywords

Cyber Security, Flask, Python, OTP Authentication, Blum Blum Shub, Cryptography, Secure Authentication, CSPRNG, Security Project, Web Security, Authentication System

