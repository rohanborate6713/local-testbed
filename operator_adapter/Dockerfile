FROM python:3.12-slim

WORKDIR /app

COPY operator_adapter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY operator_adapter/app.py .

CMD ["python", "app.py"]