#! /usr/bin/bash
export $(cat .env | xargs)
PLANER_DEBUG=True python manage.py runserver 8000
