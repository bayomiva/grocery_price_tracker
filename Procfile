web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn grocery_tracker.wsgi --bind 0.0.0.0:$PORT

