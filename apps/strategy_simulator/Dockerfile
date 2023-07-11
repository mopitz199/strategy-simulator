FROM python

RUN mkdir /home/app
WORKDIR /home/app
COPY . .
EXPOSE 8000
RUN pip3 install -r requirements.txt --no-cache-dir

WORKDIR /home/app/strategy_simulator
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]