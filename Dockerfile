FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]