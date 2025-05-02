FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS="/credentials/twiliosacstate-3cdfaefd910c.json"

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]

