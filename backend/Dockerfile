FROM python:3.7-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
ENTRYPOINT ["/django-entrypoint.sh"] 
CMD ["gunicorn", "foodgram_app.wsgi:application", "--bind", "0:8000" ] 