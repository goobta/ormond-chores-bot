FROM python:3.9-slim

RUN apt update \
    && apt install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .
RUN pip install -U wheel setuptools pip \
    && pip install -r requirements.txt

WORKDIR /proj
CMD [ "python", "src/bot.py" ]