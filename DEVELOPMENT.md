# Dynamic analysis

## setup
   

## architecture



# Web 
## User `webapps`

## Configuration
Tutorial: 
![1](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu)

![2](https://www.digitalocean.com/community/questions/how-to-set-up-django-app-redis-celery-a06db780-5335-493e-8158-7128ea7d2cc1)


## Frontend
![web](web)

Frontend: Javascript + HTML + CSS 
![HTML](web/package-analysis-web/package_analysis/templates/package_analysis)

![CSS + JS](web/package-analysis-web/package_analysis/static)

## Backend Django

1. Environment setup
+ Docker
+ Gunicorn
+ Celery

## Database
PostgreSQL
Celery

## Celery

```yaml
$ cat  vi /etc/systemd/system/celery.service

[Unit]
Description=Celery Worker for Packamal
After=network.target redis-server.service
# If you use RabbitMQ, change redis-server.service to rabbitmq-server.service

[Service]
Type=forking
User=pakaremon
Group=www-data
WorkingDirectory=/home/pakaremon/packamal/web/packamal
#EnvironmentFile=/etc/conf.d/celery
ExecStart=/home/pakaremon/packamal/packamalenv/bin/celery -A packamal worker --loglevel=INFO --concurrency=1 --detach --pidfile=/run/celery/worker.pid
#ExecStop=/home/pakaremon/packamal/packamalenv/bin/celery control shutdown
#PIDFile=/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target

```




### Components

+ Media: save current database 

#### Dynamic analysis
#### OSS-detect-backdoor
#### Bandit4mal
#### LastPyMile
#### Py2Src




## architecture

## Setup

## Backend Django: 
![1](web/package-analysis-web/packamal/settings.py)
## Database

## Gunicorn

## Nginx


# Microservices & kubernetes

