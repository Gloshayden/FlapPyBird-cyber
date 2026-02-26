FROM python:3.12-alpine

ADD server.py .
ADD requirements.txt .

RUN pip install -r requirements.txt
CMD ["fastapi", "run", "./server.py"]
