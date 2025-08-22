FROM python:3.9-slim
COPY app/requirements.txt /ProjectText2Title/app/
RUN pip install -r /ProjectText2Title/app/requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/ProjectText2Title"
WORKDIR /ProjectText2Title
CMD ["python", "app/api.py"]
