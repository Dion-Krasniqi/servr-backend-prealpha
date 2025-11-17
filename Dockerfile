FROM python:3.12
WORKDIR /main-d
COPY ./requirements.txt /main-d/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /main-d/requirements.txt
COPY ./main /main-d/main
CMD ["fastapi", "run", "main/main.py", "--port", "80"]
