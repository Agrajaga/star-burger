#!/bin/bash
set -e
echo "Set environments..."
export $(cat .env | grep ROLLBAR_ENV)
export $(cat .env | grep ROLLBAR_KEY)
echo "Update repo from GitHub..."
git pull
echo "Install Python requrements..."
source starburger_venv/bin/activate
pip install -r requirements.txt
echo "Install JS requirements..."
npm ci
echo "Build JS modules..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Collect static files..."
python manage.py collectstatic --noinput --clear
echo "Prepare database..."
python manage.py migrate --noinput --check
echo "Restart services..."
sudo systemctl restart starburger
sudo systemctl reload nginx
echo "Success!"

curl -H "X-Rollbar-Access-Token: $ROLLBAR_KEY" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d "{'environment': $ROLLBAR_ENV, 'revision': $(git rev-parse --short HEAD), 'local_username': $(git config user.name), 'comment': ${1-}, 'status': 'succeeded'}'