# AWS User Registration Application with Amazon RDS

A Python Flask-based user registration application deployed on an AWS EC2 instance, with Amazon RDS for MySQL as the backend database and Nginx as a reverse proxy.

This project demonstrates how to deploy a web application on AWS, securely connect it to a private RDS database, manage source code with Git and GitHub, and configure services to start automatically.

## Table of Contents

* [Project Overview](#project-overview)
* [Architecture](#architecture)
* [Technologies Used](#technologies-used)
* [Prerequisites](#prerequisites)
* [Phase 1: Install Git and Python on Windows](#phase-1-install-git-and-python-on-windows)
* [Phase 2: Create the Application](#phase-2-create-the-application)
* [Phase 3: Upload the Project to GitHub](#phase-3-upload-the-project-to-github)
* [Phase 4: Create the AWS Database](#phase-4-create-the-aws-database)
* [Phase 5: Launch and Configure EC2](#phase-5-launch-and-configure-ec2)
* [Phase 6: Create the Database Table](#phase-6-create-the-database-table)
* [Phase 7: Deploy the Application](#phase-7-deploy-the-application)
* [Phase 8: Configure Systemd and Nginx](#phase-8-configure-systemd-and-nginx)
* [Phase 9: Test the Application](#phase-9-test-the-application)
* [Phase 10: Update and Redeploy the Application](#phase-10-update-and-redeploy-the-application)
* [Security Best Practices](#security-best-practices)
* [Troubleshooting](#troubleshooting)
* [Cleanup](#cleanup)

## Project Overview

The application allows users to submit their registration details through a web form. The submitted information is stored in an Amazon RDS MySQL database.

### Application features

* User registration form.
* Store full name, email, phone number, and city.
* Persistent data storage using Amazon RDS for MySQL.
* Secure database connectivity using TLS.
* Nginx reverse proxy.
* Gunicorn application server.
* Systemd service for automatic application startup.
* Git and GitHub-based source code management.

## Architecture

```text
                 User / Web Browser
                         |
                         | HTTP :80
                         v
                 AWS EC2 Instance
                         |
                         v
                      Nginx
                         |
                         | 127.0.0.1:5000
                         v
                 Gunicorn + Flask
                         |
                         | MySQL :3306 over TLS
                         v
                  Amazon RDS MySQL
                         |
                         v
                 registration_db
                         |
                         v
                      users table
```

GitHub stores the application source code and is used to deploy code updates to EC2.

## Technologies Used

| Technology           | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| AWS EC2              | Hosts the application                            |
| Amazon RDS for MySQL | Stores registration data                         |
| Amazon VPC           | Provides network isolation                       |
| Security Groups      | Control inbound database and application traffic |
| Python               | Application programming language                 |
| Flask                | Web application framework                        |
| PyMySQL              | Connects Flask to MySQL                          |
| Gunicorn             | Runs the Flask application                       |
| Nginx                | Reverse proxy and HTTP entry point               |
| Git                  | Version control                                  |
| GitHub               | Remote source code repository                    |
| systemd              | Manages application startup and restarts         |

## Prerequisites

Before starting, ensure you have:

* An AWS account.
* A GitHub account.
* Git installed on Windows.
* Python installed on Windows.
* Basic knowledge of Linux commands.
* Basic understanding of EC2, VPC, security groups, and RDS.

**Important:** This is a learning project. For production use, implement HTTPS, managed secrets, input validation, restricted administrative access, and appropriate monitoring.

---

## Phase 1: Install Git and Python on Windows

### Step 1: Install Git

Download Git from the official website:

https://git-scm.com/downloads

1. Download the Windows installer.
2. Run the installer.
3. Keep the default settings unless you have a specific requirement.
4. Complete the installation.

Verify the installation in PowerShell:

```powershell
git --version
```

### Step 2: Configure Git

Replace the example values with your details.

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Verify the configuration:

```powershell
git config --global --list
```

### Step 3: Install Python

Download Python from:

https://www.python.org/downloads/

During installation, enable **Add Python to PATH**.

Verify the installation:

```powershell
python --version
pip --version
```

---

## Phase 2: Create the Application

### Step 4: Create the project directory

Open PowerShell and run:

```powershell
mkdir user-registration-app
cd user-registration-app
mkdir templates
```

The project structure will be:

```text
user-registration-app/
├── app.py
├── requirements.txt
├── .gitignore
└── templates/
    └── index.html
```

### Step 5: Create `requirements.txt`

Add the following dependencies:

```text
Flask
PyMySQL
python-dotenv
gunicorn
```

### Step 6: Create `.gitignore`

This file prevents local environment files and Python-generated files from being committed to Git.

```gitignore
.env
venv/
.venv/
__pycache__/
*.py[cod]
```

### Step 7: Create `app.py`

```python
import os

from flask import Flask, render_template, request
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        ssl_ca=os.environ.get("DB_SSL_CA") or None,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()

        if not full_name or not email:
            return "Full name and email are required.", 400

        conn = None

        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO users
                    (full_name, email, phone, city)
                    VALUES (%s, %s, %s, %s)
                """

                cursor.execute(
                    sql,
                    (full_name, email, phone or None, city or None),
                )

            conn.commit()

            return "Registration Successful!"

        except pymysql.err.IntegrityError:
            return "This email address is already registered.", 409

        except pymysql.MySQLError:
            app.logger.exception("Database operation failed")
            return "Unable to process registration. Please try again.", 500

        finally:
            if conn:
                conn.close()

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
```

The application uses parameterized SQL queries to help prevent SQL injection. It also avoids displaying raw database errors to users.

### Step 8: Create `templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Registration</title>
</head>
<body>
    <h2>User Registration Form</h2>

    <form action="/" method="POST">
        <label for="full_name">Full Name:</label><br>
        <input
            type="text"
            id="full_name"
            name="full_name"
            maxlength="100"
            required
        ><br><br>

        <label for="email">Email:</label><br>
        <input
            type="email"
            id="email"
            name="email"
            maxlength="255"
            required
        ><br><br>

        <label for="phone">Phone:</label><br>
        <input
            type="text"
            id="phone"
            name="phone"
            maxlength="20"
        ><br><br>

        <label for="city">City:</label><br>
        <input
            type="text"
            id="city"
            name="city"
            maxlength="100"
        ><br><br>

        <button type="submit">Submit Registration</button>
    </form>
</body>
</html>
```

### Step 9: Test the application locally

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the application:

```powershell
python app.py
```

Open the following URL:

http://127.0.0.1:5000

Verify that the registration form appears. Since the database environment variables have not yet been configured, a registration submission will not work until database connectivity is established.

Stop the local application with `Ctrl+C`.

---

## Phase 3: Upload the Project to GitHub

### Step 10: Create a GitHub repository

1. Open https://github.com.
2. Click **New repository**.
3. Enter `user-registration-app` as the repository name.
4. Select **Private**.
5. Leave README, `.gitignore`, and License unchecked because these files are being created locally.
6. Click **Create repository**.

### Step 11: Push the application code

Run these commands from your local project directory:

```powershell
git init -b main
git add .
git status
```

Verify that `.env` and virtual environment directories are not included.

Create the first commit:

```powershell
git commit -m "Initial user registration application"
```

Connect your repository:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/user-registration-app.git
```

Push the code:

```powershell
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

**Security note:** Never commit database passwords, AWS credentials, `.env` files, or private keys to GitHub.

---

## Phase 4: Create the AWS Database

### Step 12: Create an RDS MySQL instance

In the AWS Management Console:

1. Open **Amazon RDS**.
2. Select **Databases → Create database**.
3. Choose **Standard create**.
4. Select **MySQL** as the engine.
5. Choose an appropriate template and instance size.
6. Set the DB instance identifier to `registration-db`.
7. Configure the master username and a strong password.
8. Set the initial database name to `registration_db`, if the creation form provides this option.
9. Select the VPC that will contain your application.
10. Set **Public access** to **No**.
11. Create or select the DB subnet group with suitable private subnets.
12. Configure the RDS security group as described below.
13. Create the database and wait until its status is **Available**.

Copy the database endpoint from the RDS database's **Connectivity & security** section.

The endpoint is similar to:

```text
registration-db.xxxxxxxxxxxx.ap-south-1.rds.amazonaws.com
```

Use the actual endpoint from your AWS account.

### Step 13: Configure security groups

Create an EC2 security group named:

`registration-app-sg`

Configure its inbound rules:

| Type | Port | Source                                                                |
| ---- | ---: | --------------------------------------------------------------------- |
| HTTP |   80 | Your IP for testing, or `0.0.0.0/0` for a publicly accessible website |
| SSH  |   22 | Your IP only, if using SSH                                            |

If you use AWS Systems Manager Session Manager, you can avoid opening inbound SSH access.

For the RDS security group, named `rds-registration-sg`, configure:

| Type         | Port | Source                |
| ------------ | ---: | --------------------- |
| MySQL/Aurora | 3306 | `registration-app-sg` |

Select the EC2 security group as the source instead of allowing MySQL access from the entire internet.

Ensure both resources are in the same VPC and that routing and network ACLs permit the connection.

---

## Phase 5: Launch and Configure EC2

### Step 14: Launch an EC2 instance

1. Open **EC2 → Instances → Launch instances**.
2. Set the instance name to `registration-app-server`.
3. Select an Ubuntu Server LTS AMI.
4. Choose an instance type appropriate for a small test workload.
5. Select the same VPC used by RDS.
6. Select a public subnet for this initial deployment.
7. Enable a public IPv4 address if accessing the site directly over the internet.
8. Attach `registration-app-sg`.
9. Launch the instance.
10. Connect using SSH or Systems Manager Session Manager.

For production, a private application subnet behind an Application Load Balancer is preferable to exposing the application instance directly.

### Step 15: Install packages on EC2

Run the following commands on the Ubuntu instance:

```bash
sudo apt update

sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  nginx \
  mysql-client \
  wget
```

---

## Phase 6: Create the Database Table

### Step 16: Download the Amazon RDS CA bundle

On EC2:

```bash
cd /home/ubuntu

wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

### Step 17: Connect to RDS

Replace `YOUR_RDS_ENDPOINT` with the actual endpoint.

```bash
mysql \
  -h YOUR_RDS_ENDPOINT \
  -u dbadmin \
  -p \
  --ssl-mode=VERIFY_IDENTITY \
  --ssl-ca=/home/ubuntu/global-bundle.pem
```

Enter the database password when prompted.

If your MySQL client does not support these SSL options, install a compatible client or use a client that supports certificate and hostname verification.

### Step 18: Create the database and table

Run the following SQL commands inside the MySQL prompt:

```sql
CREATE DATABASE IF NOT EXISTS registration_db;

USE registration_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;

EXIT;
```

The `users` table stores each registration, while `created_at` records when the record was created.

If the database was already created through the RDS console, the `CREATE DATABASE IF NOT EXISTS` command will leave it intact.

---

## Phase 7: Deploy the Application

### Step 19: Clone the GitHub repository

On EC2:

```bash
cd /home/ubuntu

git clone https://github.com/YOUR-USERNAME/user-registration-app.git

cd user-registration-app
```

For a private repository, configure an appropriate authentication method. Do not embed personal access tokens in the clone URL or store them in application files.

### Step 20: Create a Python virtual environment

```bash
cd /home/ubuntu/user-registration-app

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Step 21: Configure environment variables

Create the environment file:

```bash
nano /home/ubuntu/user-registration-app/.env
```

Add the following configuration:

```dotenv
DB_HOST=YOUR_RDS_ENDPOINT
DB_PORT=3306
DB_NAME=registration_db
DB_USER=dbadmin
DB_PASSWORD=YOUR_DATABASE_PASSWORD
DB_SSL_CA=/home/ubuntu/global-bundle.pem
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
```

Replace all placeholder values with your actual configuration.

Generate a random secret for the application rather than using the example value. For production, use AWS Secrets Manager or another appropriate secret-management mechanism.

Restrict permissions:

```bash
chmod 600 /home/ubuntu/user-registration-app/.env
```

Verify the file permissions:

```bash
ls -l /home/ubuntu/user-registration-app/.env
```

The application user must be able to read this file. Do not print the contents of `.env` in logs or share them publicly.

---

## Phase 8: Configure Systemd and Nginx

### Step 22: Create a systemd service

Create the service file:

```bash
sudo nano /etc/systemd/system/registration.service
```

Add:

```ini
[Unit]
Description=User Registration Application
Wants=network-online.target
After=network-online.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/user-registration-app
EnvironmentFile=/home/ubuntu/user-registration-app/.env
ExecStart=/home/ubuntu/user-registration-app/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save the file and reload systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now registration
```

Check the service:

```bash
sudo systemctl status registration
```

If the service fails, inspect the logs:

```bash
sudo journalctl -u registration -n 100 --no-pager
```

Gunicorn listens only on `127.0.0.1:5000`, so the application port does not need to be publicly exposed.

### Step 23: Configure Nginx as a reverse proxy

Create the Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/registration
```

Add:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
sudo ln -sf \
  /etc/nginx/sites-available/registration \
  /etc/nginx/sites-enabled/registration
```

Remove the default site if it is still enabled:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

Test the Nginx configuration:

```bash
sudo nginx -t
```

If the test succeeds, enable and reload Nginx:

```bash
sudo systemctl enable nginx
sudo systemctl reload nginx
```

---

## Phase 9: Test the Application

### Step 24: Access the website

1. Open the EC2 console.
2. Select `registration-app-server`.
3. Copy its public IPv4 address.
4. Open the following URL in your browser:

```text
http://YOUR_EC2_PUBLIC_IP
```

The user registration form should appear.

### Step 25: Submit a registration

Enter a name, email, phone number, and city.

Submit the form. A successful submission should display:

```text
Registration Successful!
```

Submitting the same email address again should return a duplicate-email message because the database enforces a unique constraint.

### Step 26: Verify the record in RDS

From EC2, connect to MySQL:

```bash
mysql \
  -h YOUR_RDS_ENDPOINT \
  -u dbadmin \
  -p \
  --ssl-mode=VERIFY_IDENTITY \
  --ssl-ca=/home/ubuntu/global-bundle.pem
```

Run:

```sql
USE registration_db;

SELECT * FROM users ORDER BY id DESC;

EXIT;
```

Confirm that the submitted registration appears in the results.

### Step 27: Troubleshoot common issues

Check the application service:

```bash
sudo systemctl status registration

sudo journalctl -u registration -n 100 --no-pager
```

Check Nginx:

```bash
sudo systemctl status nginx

sudo nginx -t

sudo tail -n 100 /var/log/nginx/error.log
```

Test the Flask application locally on EC2:

```bash
curl -i http://127.0.0.1:5000/
```

Test the public Nginx endpoint:

```bash
curl -i http://127.0.0.1/
```

If the application cannot connect to RDS, verify:

* The RDS endpoint, port, database name, username, and password.
* The RDS security group allows TCP port 3306 from `registration-app-sg`.
* Both resources use the intended VPC.
* The database is in the **Available** state.
* The CA bundle exists and the database connection uses TLS certificate verification.
* The database user has the required permissions.

If the default Nginx page appears, check whether the default site was disabled and whether the registration site configuration was enabled successfully.

---

## Phase 10: Update and Redeploy the Application

### Step 28: Update code locally

Make the required changes to your application.

From PowerShell inside the project directory:

```powershell
git status

git add .

git commit -m "Update registration application"

git push origin main
```

### Step 29: Pull changes on EC2

Connect to EC2 and run:

```bash
cd /home/ubuntu/user-registration-app

git pull --ff-only origin main
```

If dependencies have changed:

```bash
source venv/bin/activate

pip install -r requirements.txt
```

Restart the application:

```bash
sudo systemctl restart registration
```

Check its status:

```bash
sudo systemctl status registration

sudo journalctl -u registration -n 50 --no-pager
```

Nginx normally does not need to be restarted for Python application code changes.

**Deployment note:** This is a basic manual deployment workflow. A production pipeline should include automated tests, dependency management, rollback procedures, and controlled deployments.

---

## Security Best Practices

For a more production-oriented implementation, consider these improvements:

1. **Private database:** Keep RDS private and allow port 3306 only from the application security group.
2. **HTTPS:** Use an Application Load Balancer with an ACM certificate for HTTPS.
3. **Secrets management:** Store database credentials in AWS Secrets Manager rather than maintaining long-lived passwords in a local environment file.
4. **Least privilege:** Use a dedicated application database user with only the necessary permissions instead of the RDS master user.
5. **Network isolation:** Place application instances in private subnets behind a load balancer when appropriate.
6. **Application validation:** Add server-side validation, rate limiting, and CSRF protection.
7. **Monitoring:** Use Amazon CloudWatch logs, metrics, alarms, and relevant RDS monitoring features.
8. **Backups:** Configure suitable RDS automated backups and test database restoration.
9. **Patch management:** Keep Ubuntu packages and application dependencies updated.
10. **Git security:** Keep secrets, private keys, and credentials out of version control.
11. **Availability:** For a production service, consider a load balancer and an Auto Scaling group spanning multiple Availability Zones.

## Cleanup

To avoid ongoing AWS charges after completing the lab:

1. Back up any registration data you want to keep.
2. Delete the EC2 instance if you no longer need it.
3. Delete the RDS instance after confirming that its data is no longer required.
4. Review and remove unused EBS volumes, snapshots, Elastic IP addresses, and other billable resources.
5. Check the AWS Billing and Cost Management console for remaining charges.

Take care when deleting RDS resources: deletion can permanently remove data if no backup is retained.

## Learning Outcomes

After completing this project, you should understand how to:

* Build a basic Flask web application.
* Use Git and GitHub for source code management.
* Deploy a Python application to an EC2 instance.
* Configure Amazon RDS for MySQL.
* Connect an application to a private database using security groups.
* Configure database TLS verification.
* Use Nginx as a reverse proxy.
* Run applications with Gunicorn and systemd.
* Verify application data in a relational database.
* Perform basic application updates and redeployments.
# flask-application-form-application
# flask-application-form-application
