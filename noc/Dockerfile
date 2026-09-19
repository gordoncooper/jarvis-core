FROM python:3.12-alpine
WORKDIR /app
COPY collector/server.py /app/collector/server.py
COPY ui/index.html /app/ui/index.html
ENV PORT=8080 NOC_VERSION=v0.1.0
EXPOSE 8080
USER 65532:65532
CMD ["python3", "/app/collector/server.py"]
