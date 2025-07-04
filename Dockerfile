FROM python:3.11-slim

WORKDIR /app
COPY ./app /app/app
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
EXPOSE 5005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5005"]
