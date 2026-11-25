# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

---

# 📝 7. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)


---

# Module 10: Secure User Model and Docker Deployment

## Overview

This project extends my existing IS 601 FastAPI Calculator
with a secure user model, input validation, database testing,
and automated Docker deployment.

## Features

- SQLAlchemy User model with unique usernames and emails
- Secure password hashing using Argon2 through pwdlib
- Password verification
- Pydantic validation for user registration data
- UserRead schema that excludes password hashes
- Duplicate username and email protection
- SQLite unit tests
- PostgreSQL integration tests
- Automated testing with GitHub Actions
- Docker image publishing to Docker Hub

## Technologies Used

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL 16
- SQLite
- Pytest
- Docker
- GitHub Actions

## Running the Application

Install dependencies:

    pip install -r requirements.txt

Start the FastAPI calculator:

    uvicorn main:app --reload

Open the application at:

http://localhost:8000

## Testing

Run the complete test suite:

    python -m pytest -q

PostgreSQL integration tests use a dedicated database named
module10_test. Configure TEST_DATABASE_URL to run them.

Example local test connection:

    export TEST_DATABASE_URL="postgresql+psycopg://module10_test:local_test_only@127.0.0.1:5434/module10_test"

Run PostgreSQL integration tests:

    python -m pytest tests/test_users_postgres.py -v

## Docker Deployment

Docker Hub repository:

https://hub.docker.com/r/brownie97/module10-fastapi

Pull the published Docker image:

    docker pull brownie97/module10-fastapi:latest

Run the Docker container:

    docker run --rm -p 8001:8000 brownie97/module10-fastapi:latest

Open the calculator at:

http://localhost:8001

## Continuous Integration and Deployment

GitHub Actions automatically runs the application's tests,
including PostgreSQL integration tests.

When the tests pass on the module10-secure-users branch,
GitHub Actions builds and publishes the Docker image.

Docker Hub authentication uses encrypted GitHub Actions
repository secrets.

## GitHub Repository

https://github.com/iamnigeria-bit/IS601-Module8-FastAPI-Calculator

Module 10 development branch:

module10-secure-users


---

# Module 11: Calculation Model and Factory Pattern

## Overview

Module 11 extends the FastAPI Calculator with a SQLAlchemy
Calculation model, Pydantic validation, and a calculation
factory pattern.

## Features

- Calculation model with id, a, b, type, and result
- Four supported operations: add, sub, multiply, divide
- Pydantic CalculationCreate and CalculationRead schemas
- Validation for unsupported operations and division by zero
- Factory pattern for selecting mathematical operations
- Calculation service for saving results to the database
- SQLite unit tests
- PostgreSQL integration tests
- Automated GitHub Actions testing
- Trivy Docker image security scanning
- Automated Docker Hub deployment

## Running Tests Locally

Install dependencies:

    python -m pip install -r requirements.txt

Run all tests:

    python -m pytest -q

To run PostgreSQL integration tests, start the dedicated
PostgreSQL test database and configure TEST_DATABASE_URL.

Run calculation unit tests:

    python -m pytest tests/test_calculations.py -v

Run calculation PostgreSQL integration tests:

    python -m pytest tests/test_calculations_postgres.py -v

The PostgreSQL tests require TEST_DATABASE_URL to be set.

## Docker Hub

Docker Hub repository:

https://hub.docker.com/r/brownie97/module10-fastapi

Pull the Module 11 image:

    docker pull --platform linux/amd64 brownie97/module10-fastapi:module11

Run the image:

    docker run --rm --platform linux/amd64 -p 8002:8000 brownie97/module10-fastapi:module11

Open the calculator at:

http://localhost:8002

## CI/CD Pipeline

GitHub Actions runs the automated test suite with PostgreSQL.
After successful tests, the Docker image is scanned with
Trivy before publication to Docker Hub.

## GitHub Repository

https://github.com/iamnigeria-bit/IS601-Module8-FastAPI-Calculator/tree/module11-calculation-model

## Future Development

Module 12 will extend the calculation functionality with
API endpoints for creating, retrieving, updating, and
deleting calculation records.

---

# Module 12: User and Calculation Routes

## Overview

Module 12 completes the FastAPI calculator backend by
implementing secure user registration, login, calculation
BREAD operations, and automated integration testing.

## Features

- User registration with secure Argon2 password hashing
- User login with password verification
- SQLAlchemy database integration
- Pydantic request and response validation
- Calculation BREAD operations
- Duplicate account prevention
- Database transaction rollback
- Automated PostgreSQL integration testing
- GitHub Actions CI/CD
- Docker image security scanning and publication

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /users/register | Register a user |
| POST | /users/login | Verify login credentials |
| GET | /calculations | Browse calculations |
| GET | /calculations/{id} | Read a calculation |
| PUT | /calculations/{id} | Edit a calculation |
| POST | /calculations | Add a calculation |
| DELETE | /calculations/{id} | Delete a calculation |

Login verifies credentials without issuing session tokens.
Token-based authorization is outside the Module 12 scope.

## Run Locally

Requires Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Manual API Testing

Open Swagger UI:

http://127.0.0.1:8000/docs

Alternative API documentation:

http://127.0.0.1:8000/redoc

Use Swagger UI's Try it out and Execute buttons
to register a user, verify login credentials, and
create, browse, read, edit, and delete calculations.

## Automated Testing

Run Module 12 integration tests:

```bash
python -m pytest tests/integration/test_module12_routes.py -v
```

Install Playwright Chromium and run the full suite:

```bash
python -m playwright install chromium
python -m pytest -q
```

Local verification results:

- 20 new integration tests passed
- 67 total tests passed
- 10 PostgreSQL tests skipped locally
- 91% overall application code coverage
- Zero failed tests

GitHub Actions configures TEST_DATABASE_URL and runs
the integration tests using a dedicated PostgreSQL
test database before publishing the Docker image.

## Docker Hub

Repository:
https://hub.docker.com/r/brownie97/module10-fastapi

Module 12 image:

```bash
docker pull --platform linux/amd64 brownie97/module10-fastapi:module12
```

Run the published image for local verification:

```bash
docker run --rm -p 127.0.0.1:8012:8000 \
  --platform linux/amd64 \
  -e DATABASE_URL=sqlite:////tmp/module12-smoke.db \
  brownie97/module10-fastapi:module12
```

Open http://127.0.0.1:8012/docs

## CI/CD Pipeline

GitHub Actions automatically runs tests, validates
PostgreSQL integration, builds the Docker image,
performs a Trivy security scan, and publishes the
image to Docker Hub after successful verification.
