FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
COPY app_v2.py /app/app_v2.py
COPY site_custom.py /app/site_custom.py
COPY run_brand.py /app/run_brand.py
COPY run_faces.py /app/run_faces.py
COPY static /app/static
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 8080
CMD ["python", "run_faces.py"]
