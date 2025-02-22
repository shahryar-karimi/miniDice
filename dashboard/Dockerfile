# Use a base image with Python
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install -r /app/requirements.txt

# Copy the rest of the application files
COPY . /app

# Expose the port Streamlit will use
EXPOSE 8501

RUN chmod +x /app/entrypoint.sh
# Set the default command
ENTRYPOINT ["/app/entrypoint.sh"]
