#!/usr/bin/env bash
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Applying migrations..."
python manage.py migrate
