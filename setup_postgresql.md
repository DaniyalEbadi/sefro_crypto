# PostgreSQL Setup Guide

## Option 1: If PostgreSQL is already installed

1. **Find your PostgreSQL password:**
   - Check if you remember the password you set during installation
   - Or reset the postgres user password

2. **Update your .env file:**
   ```
   DB_PASSWORD=your_actual_password_here
   ```

## Option 2: Set up PostgreSQL from scratch

### For Windows:

1. **Install PostgreSQL:**
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for the 'postgres' user

2. **Create database:**
   ```sql
   -- Connect to PostgreSQL as postgres user
   CREATE DATABASE uni_project;
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE uni_project TO your_user;
   ```

3. **Update .env file:**
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=uni_project
   DB_USER=your_user
   DB_PASSWORD=your_password
   ```

## Option 3: Use PostgreSQL with default settings

If you want to use the default postgres user:

1. **Set postgres user password:**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Set password
   ALTER USER postgres PASSWORD 'newpassword';
   ```

2. **Create database:**
   ```sql
   CREATE DATABASE uni_project;
   ```

3. **Update .env:**
   ```
   DB_PASSWORD=newpassword
   ```

## Option 4: Quick Docker PostgreSQL (Recommended for development)

```bash
# Run PostgreSQL in Docker
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=uni_project \
  -p 5432:5432 \
  -d postgres:13

# Then update .env:
DB_PASSWORD=devpassword
```

## Testing the connection

After updating your .env file, test the connection:

```bash
cd c:\Users\Dani\Desktop\uni_project
python manage.py check --database default
python manage.py migrate
```