FROM python:3

WORKDIR /usr/src/myapp

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python


## docker build . --tag python-download-doc
## docker run -it -v "$PWD":/usr/src/myapp python-download-doc python download-doc.py [doc id]
