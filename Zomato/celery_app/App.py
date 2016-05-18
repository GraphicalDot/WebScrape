#!/usr/bin/env python
#-*- coding: utf-8 -*-
from celery import Celery
import os
os.environ.setdefault('CELERY_CONFIG_MODULE', 'celery_app.celeryconfig')

app = Celery("celery_app")

app.config_from_envvar('CELERY_CONFIG_MODULE')


if __name__ == "__main__":
	app.start()
