FROM python:3.9.1-alpine3.12

RUN apk update
RUN apk add bash
RUN apk add vim

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "./AFexcuses.py"]

