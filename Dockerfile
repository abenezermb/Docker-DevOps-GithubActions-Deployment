# Use official Python image
FROM python:3.10-slim

# Set workdir
WORKDIR web-app

# Copy files and install dependencies
COPY web-app/requirements.txt .
RUN pip install -r requirements.txt

# # copy app.py
# COPY web-app/app.py

# Copy source code
COPY web-app .

# Expose the port and run the app
EXPOSE 5000
CMD ["python", "app.py"]
