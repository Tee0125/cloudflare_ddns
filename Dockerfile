from python:3.6-alpine

RUN pip install requests

WORKDIR /opt/ddns
ADD ddns.py /opt/ddns
 
CMD ["python3", "ddns.py"]
