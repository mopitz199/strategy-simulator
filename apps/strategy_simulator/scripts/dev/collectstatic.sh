#!/bin/bashs
docker-compose -f ../../../docker-compose-prod.yml run strategy-simulator python manage.py collectstatic --settings=strategy_simulator.settings_prod