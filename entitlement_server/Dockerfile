FROM python:3.12-slim

WORKDIR /app

COPY entitlement_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entitlement_server/app.py .
COPY entitlement_server/metrics.py .

CMD ["python", "app.py"]