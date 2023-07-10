FROM python

RUN mkdir /home/app
WORKDIR /home/app
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir