FROM python:3.13-slim
WORKDIR /dashboard
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /dashboard/entrypoint.sh
CMD ["python3", "chart.py"]
