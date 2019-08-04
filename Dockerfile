FROM python:3.7
ADD . /desafio
WORKDIR /desafio
RUN pip install  -r requirements.txt
EXPOSE      5000
EXPOSE      6379
CMD  python app.py