FROM python

LABEL maintainer = 'abdul hadi'

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY . /code/

RUN pip install -r requirements.txt

EXPOSE 8000

# Run the app. CMD can be overridden when starting the container
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--reload"]