#!/bin/bash

echo "=== Fixing Database Connection ==="
echo ""

# Check current database URL
echo "1. Checking DATABASE_URL in .env file..."
if [ -f ".env" ]; then
    grep "DATABASE_URL" .env | head -1
else
    echo "No .env file found!"
fi

echo ""
echo "2. Testing PostgreSQL connection..."

# Extract connection details from the production .env
DB_HOST="db-postgresql-fra1-29054-do-user-23461250-0.f.db.ondigitalocean.com"
DB_PORT="25060"
DB_NAME="defaultdb"
DB_USER="doadmin"

echo "Attempting to connect to:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"

# Test connection without password prompt
export PGPASSWORD="AVNS_b-Yu6tYsVvTh4GHch3B"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" 2>&1 | head -5

echo ""
echo "3. Common fixes:"
echo ""
echo "Option A - Use the full DATABASE_URL (recommended):"
echo "Make sure your .env file has:"
echo "DATABASE_URL=postgresql://doadmin:AVNS_b-Yu6tYsVvTh4GHch3B@db-postgresql-fra1-29054-do-user-23461250-0.f.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
echo ""
echo "Option B - Set PGPASSWORD environment variable:"
echo "export PGPASSWORD='AVNS_b-Yu6tYsVvTh4GHch3B'"
echo ""
echo "Option C - Create .pgpass file:"
echo "echo 'db-postgresql-fra1-29054-do-user-23461250-0.f.db.ondigitalocean.com:25060:defaultdb:doadmin:AVNS_b-Yu6tYsVvTh4GHch3B' > ~/.pgpass"
echo "chmod 600 ~/.pgpass"