FROM python:3.5-alpine
MAINTAINER Emily Benitez
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["run.py"]