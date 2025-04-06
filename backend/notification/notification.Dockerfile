FROM python:3-slim
WORKDIR /usr/src/app
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt
COPY ./notification.py .
# Healthcheck to verify the service is running properly
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5011/notification || exit 1
# Default environment variables
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672
ENV RABBITMQ_USER=guest
ENV RABBITMQ_PASSWORD=guest
CMD [ "python", "./notification.py" ]