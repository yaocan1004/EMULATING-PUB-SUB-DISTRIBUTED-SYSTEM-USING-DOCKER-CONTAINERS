FROM python:2.7


# Place app in container.
COPY . /app
WORKDIR /app

# Install dependencies.
RUN pip install -r requirements.txt

EXPOSE 5000
CMD python phase2.py