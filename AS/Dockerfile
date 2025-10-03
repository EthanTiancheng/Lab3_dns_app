FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install -r requirements.txt --no-cache-dir; fi
COPY . .
EXPOSE 53533/udp
CMD ["python", "as_server.py"]
