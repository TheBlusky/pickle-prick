FROM python:latest
RUN mkdir /pickleprick
WORKDIR /pickleprick
ADD ./application /pickleprick
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python pickleprick.py