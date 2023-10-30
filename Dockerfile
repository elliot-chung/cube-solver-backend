FROM python

COPY ./*.py /app/

EXPOSE 8080

CMD ["python", "/app/main.py"]