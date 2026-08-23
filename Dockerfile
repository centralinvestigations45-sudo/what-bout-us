FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
COPY app_v2.py /app/app_v2.py
COPY site_custom.py /app/site_custom.py
COPY static /app/static
EXPOSE 8080
CMD ["python", "site_custom.py"]
