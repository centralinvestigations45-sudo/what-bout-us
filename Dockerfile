FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
COPY app_v2.py /app/app_v2.py
COPY site_custom.py /app/site_custom.py
COPY run_nice.py /app/run_nice.py
COPY run_current.py /app/run_current.py
COPY run_profile.py /app/run_profile.py
COPY run_launch.py /app/run_launch.py
COPY run_analytics.py /app/run_analytics.py
COPY run_idle.py /app/run_idle.py
COPY run_pricing.py /app/run_pricing.py
COPY run_wallet.py /app/run_wallet.py
COPY run_topup.py /app/run_topup.py
COPY run_brand.py /app/run_brand.py
COPY run_faces.py /app/run_faces.py
COPY static /app/static
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 8080
CMD ["python", "run_faces.py"]
