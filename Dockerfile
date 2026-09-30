# Use the official Playwright image which includes all necessary Linux browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Start the FastAPI server on port 10000 (Render will route traffic here)
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-10000}
