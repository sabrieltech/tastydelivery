FROM python:3-slim
WORKDIR /usr/src/app
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt
COPY ./processCustomerPayment.py .
CMD [ "python", "./processCustomerPayment.py" ]