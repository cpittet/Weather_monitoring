FROM ubuntu

# Create script directory for the app
RUN mkdir -p /usr/src/script

#Change working directory
WORKDIR /usr/src/script

# Install libraries for the sensor
# Without sudo, because not recognized
RUN apt-get update
RUN apt-get install sense-hat

# Copy the script into the container
COPY collect.py collect.py


# Create for where to store data temporarily
RUN mkdir -p data
