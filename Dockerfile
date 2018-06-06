FROM python:3.6
WORKDIR /app
Add . /app
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]