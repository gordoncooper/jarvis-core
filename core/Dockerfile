FROM python:3.12-alpine
WORKDIR /app
COPY glass/server.py /app/glass/server.py
COPY glass/index.html /app/glass/index.html
ENV PORT=8080 CORE_VERSION=v0.2.0
EXPOSE 8080
USER 65532:65532
CMD ["python3", "/app/glass/server.py"]
