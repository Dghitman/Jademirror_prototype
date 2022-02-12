FROM python:3.9  

COPY requirements.txt /worker/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /worker/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]