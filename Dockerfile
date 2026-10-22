FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]
