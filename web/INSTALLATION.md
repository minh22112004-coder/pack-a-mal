# Installation Guide

## Prerequisites

- Ubuntu 22.04 LTS (or compatible Linux distribution)
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git

## Step 1: Clone the Project

```bash
git clone https://github.com/packguard-dev/pack-a-mal.git
cd pack-a-mal/web/package-analysis-web
```

## Step 2: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev python3-venv libpq-dev postgresql postgresql-contrib
```

## Step 3: Set Up Python Virtual Environment

Install virtualenv (if not already installed):
```bash
sudo pip3 install virtualenv
```

Create virtual environment:
```bash
python3 -m venv env
```

Activate virtual environment:
```bash
source env/bin/activate
```

## Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Set Up PostgreSQL Database

### Create Database and User

```bash
sudo -u postgres psql
```

Then run the following SQL commands:

```sql
-- Create database
CREATE DATABASE packamal;

-- Create user with password
CREATE USER pakaremon WITH PASSWORD 'rock-beryl-say-devices';

-- Configure user settings
ALTER ROLE pakaremon SET client_encoding TO 'utf8';
ALTER ROLE pakaremon SET default_transaction_isolation TO 'read committed';
ALTER ROLE pakaremon SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE packamal TO pakaremon;

-- Exit PostgreSQL
\q
```

## Step 6: Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Settings
DB_NAME=packamal
DB_USER=pakaremon
DB_PASSWORD=rock-beryl-say-devices
DB_HOST=localhost
DB_PORT=5432
```

**Note:** Replace `your-secret-key-here` with a secure secret key. You can generate one using:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Step 7: Run Django Migrations

Make sure your virtual environment is activated, then:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 8: Create Superuser (Optional)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

## Step 9: Run the Development Server

```bash
python manage.py runserver
```

## Step 10: Set Up Docker

Install prerequisites:
```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

Add Docker GPG key:
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

Add Docker to apt source:
```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Update package list:
```bash
sudo apt update
```

Check available Docker versions:
```bash
apt-cache policy docker-ce
```

Install Docker:
```bash
sudo apt install docker-ce
```

Add your user to the docker group (to run Docker without sudo):
```bash
sudo usermod -aG docker ${USER}
```

**Note:** You will need to log out and log back in (or run `su - ${USER}`) for the group changes to take effect.

## Step 11: Set Up Analysis Script

Make the analysis script executable. From the project root directory (`pack-a-mal`):
```bash
chmod +x scripts/run_analysis.sh
```

**Note:** If you're still in the `web/package-analysis-web` directory, navigate to the project root first:
```bash
cd ../../  # From web/package-analysis-web to project root
chmod +x scripts/run_analysis.sh
```

The application will be available at `http://127.0.0.1:8000/`

## Troubleshooting

- If you encounter permission errors with PostgreSQL, ensure the user has proper permissions
- If you see database connection errors, verify your `.env` file has correct database credentials
- Make sure your virtual environment is activated before running Django commands
- For production deployment, set `DEBUG=False` and configure proper `ALLOWED_HOSTS`

## Next Steps

- Review the [API Documentation](API_DOCUMENTATION.md) for API endpoints
- Check the [Architecture Diagram](ARCHITECTURE_DIAGRAM.md) for system overview
- Read the [Queue System README](QUEUE_SYSTEM_README.md) for queue configuration


