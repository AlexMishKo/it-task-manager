#!/usr/bin/env bash
#Exit on error
set -o errexit

#Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

#Convert static asset files
python manage.py collectstatic --no-input

#Apply ant outstanding database migrations
python manage.py migrate

#Creating superuser cz Shell is not available in free render
python manage.py shell -c "from manager.models import Worker;
Worker.objects.create_superuser(
'admin_render',
'admin@example.com',
'YourPassword123')
if not Worker.objects.filter(username='admin_render').exists() else print('Admin exists')"

#Loading data
python manage.py loaddata dump.json