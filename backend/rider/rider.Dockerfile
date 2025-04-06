FROM python:3-slim
WORKDIR /usr/src/app
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt
COPY ./rider.py .
ENV API_URL="https://personal-g86bdbq5.outsystemscloud.com/Rider/rest/v1"
CMD [ "python", "./rider.py" ]