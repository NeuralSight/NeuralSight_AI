
# create the db
# #
# if [ -z "$1" ]; then
#   echo "no database specified. aborting."
#   exit
# fi
#
# sudo su postgres <<EOF
# psql -c "CREATE USER $1 WITH PASSWORD '$1';"
# CREATE DATABASE '$1';
# echo "Postgres user and database '$1' created."
# EOF

# sudo apt install postgresql-client-common -y
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service

DB_NAME=$(grep DB_NAME .env | cut -d '=' -f 2-)
DB_USER=$(grep DB_USER .env | cut -d '=' -f 2-)
DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f 2-)

echo $DB_NAME;
echo $DB_USER;
echo $DB_PASSWORD;

sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
