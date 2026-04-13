FROM python:3.13-slim
WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "chart.py"]
