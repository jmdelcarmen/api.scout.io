FROM python:3

WORKDIR /usr/src

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD [ "python3", "/usr/src/run.py" ]