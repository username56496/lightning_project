FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
# 👇 아래처럼 --trusted-host 옵션들을 추가해 줍니다!
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]