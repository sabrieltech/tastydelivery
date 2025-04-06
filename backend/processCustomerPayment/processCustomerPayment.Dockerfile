FROM python:3-slim
WORKDIR /usr/src/app
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt
COPY ./processCustomerPayment.py .
VOLUME /usr/src/app/data
RUN mkdir -p /usr/src/app/data && chmod 777 /usr/src/app/data
WORKDIR /usr/src/app
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5020/circuit_status || exit 1

CMD [ "python", "./processCustomerPayment.py" ]