until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python manage.py makemigrations
python manage.py makemigrations ourapp
python manage.py migrate
python manage.py shell < scripts/init_db.py
python manage.py shell < ourapp/utils.py
python manage.py runserver 0.0.0.0:8000