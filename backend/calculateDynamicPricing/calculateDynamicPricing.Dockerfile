FROM python:3-slim
WORKDIR /usr/src/app

# Install Node.js to run the Google Maps service
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install npm packages
COPY ./googleMapsService.js ./
RUN npm install axios

# Install Python requirements
COPY http-reqs-file.txt ./
RUN python -m pip install --no-cache-dir -r http-reqs-file.txt

# Copy application code
COPY ./calculateDynamicPricing.py ./

CMD [ "python", "./calculateDynamicPricing.py" ]