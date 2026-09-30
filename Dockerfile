# Use the official Playwright image which includes all necessary Linux browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Set the working directory
WORKDIR /app

# Copy the requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the agent code
COPY . .

# Run the agent
CMD ["python", "main.py"]
