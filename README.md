# Oceana Backend

Simple Flask API for OceanaGPT.

## Run locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OCEANA_MW_KEY=test123
python app.py

## API test
GET http://127.0.0.1:5000/v1/ocean/point?lat=15.5&lon=89.2  
Header → Authorization: Bearer test123

