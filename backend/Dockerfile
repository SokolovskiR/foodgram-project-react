FROM python:3.7-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app/
RUN pip3 install -r requirements.txt --no-cache-dir
ENTRYPOINT ["django-entrypoint.sh"] 