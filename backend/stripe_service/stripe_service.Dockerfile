FROM python:3-slim
WORKDIR /usr/src/app
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt
RUN pip install stripe
COPY ./stripe_service.py .
CMD [ "python", "./stripe_service.py" ]