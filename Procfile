web: python manage.py setup_db && python manage.py collectstatic --noinput && gunicorn grocery_tracker.wsgi --bind 0.0.0.0:$PORT

