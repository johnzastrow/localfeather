#!/bin/bash
# ============================================================================
# Local Feather - Database Setup Script
# ============================================================================
# Quick setup script for MariaDB database
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "Local Feather - Database Setup"
echo "=============================================="
echo ""

# Check if config.ini exists
if [ ! -f "config.ini" ]; then
    echo -e "${YELLOW}Creating config.ini from example...${NC}"
    cp config.example.ini config.ini
    echo -e "${GREEN}✓${NC} Created config.ini"
    echo ""
    echo -e "${RED}IMPORTANT:${NC} Edit config.ini with your MariaDB credentials!"
    echo "  nano config.ini"
    echo ""
    read -p "Press Enter when you've updated config.ini..."
fi

# Read database credentials from config.ini
DB_HOST=$(grep "^host" config.ini | cut -d'=' -f2 | tr -d ' ')
DB_PORT=$(grep "^port" config.ini | cut -d'=' -f2 | tr -d ' ')
DB_NAME=$(grep "^database" config.ini | cut -d'=' -f2 | tr -d ' ')
DB_USER=$(grep "^username" config.ini | cut -d'=' -f2 | tr -d ' ')

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Prompt for root password
echo "Enter MariaDB root password (for database creation):"
read -s MYSQL_ROOT_PASSWORD
echo ""

# Test connection
echo -e "${YELLOW}Testing MariaDB connection...${NC}"
if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to MariaDB server${NC}"
    echo "Please check:"
    echo "  - MariaDB is running: systemctl status mariadb"
    echo "  - Host and port are correct in config.ini"
    echo "  - Root password is correct"
    exit 1
fi
echo -e "${GREEN}✓${NC} MariaDB connection successful"
echo ""

# Create database and user
echo -e "${YELLOW}Creating database and user...${NC}"

# Get user password from config
DB_PASSWORD=$(grep "^password" config.ini | cut -d'=' -f2 | tr -d ' ')

mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
-- Create database
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';

-- Grant permissions
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;

-- Show result
SELECT CONCAT('✓ Database: ', SCHEMA_NAME) AS Result
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME = '$DB_NAME';

SELECT CONCAT('✓ User: ', user, '@', host) AS Result
FROM mysql.user
WHERE user = '$DB_USER';
EOF

echo -e "${GREEN}✓${NC} Database and user created"
echo ""

# Import schema
echo -e "${YELLOW}Importing database schema...${NC}"
if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < schema.sql; then
    echo -e "${GREEN}✓${NC} Schema imported successfully"
else
    echo -e "${RED}❌ Schema import failed${NC}"
    exit 1
fi
echo ""

# Ask about seeding data
echo "Do you want to seed the database with test data? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Seeding database...${NC}"

    # Check if Python and pip are available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        echo "Please install Python 3 and run: python3 seed_data.py"
        exit 1
    fi

    # Check if dependencies are installed
    if ! python3 -c "import sqlalchemy" &> /dev/null; then
        echo "Installing Python dependencies..."
        pip3 install sqlalchemy pymysql werkzeug
    fi

    # Run seed script
    if python3 seed_data.py; then
        echo -e "${GREEN}✓${NC} Database seeded with test data"
    else
        echo -e "${RED}❌ Seeding failed${NC}"
    fi
else
    echo "Skipping seed data"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✓ Database setup complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Test connection: python3 -c \"from app.database import init_db; init_db().health_check()\""
echo "  2. Start Flask server (when implemented)"
echo ""
echo "Default test credentials (if seeded):"
echo "  Admin:  username=admin,  password=admin123"
echo "  Viewer: username=viewer, password=viewer123"
echo ""
echo -e "${RED}IMPORTANT:${NC} Change default passwords in production!"
echo "=============================================="
