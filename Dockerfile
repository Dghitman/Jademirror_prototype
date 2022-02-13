FROM python:3.9  

COPY requirements.txt /worker/requirements.txt

COPY install_stanza.py /worker/install_stanza.py

RUN pip install --no-cache-dir --upgrade -r /worker/requirements.txt

RUN python /worker/install_stanza.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]