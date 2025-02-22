# Use a base image with Python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY reqs.txt /app/reqs.txt

# Install the dependencies
RUN pip install -r /app/reqs.txt

# Copy the rest of the application files
COPY . /app

# Expose the port Streamlit will use
EXPOSE 8501

RUN chmod +x /app/entrypoint.sh
# Set the default command
CMD ["sh", "/app/entrypoint.sh"]
