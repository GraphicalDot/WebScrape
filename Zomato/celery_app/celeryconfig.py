import os
from kombu import Exchange, Queue
from celery.schedules import crontab
#from kombu import serialization
#serialization.registry._decoders.pop("application/x-python-serialize")
#BROKER_URL = 'redis://'
BROKER_URL = 'redis://localhost:6379/0'

CELERY_QUEUES = (
		Queue('StartScrapeChainQueue', Exchange('default', delivery_mode= 2),  routing_key='StartScrapeChainQueue.import'),
		Queue('GenerateEateriesListQueue', Exchange('default', delivery_mode= 2),  routing_key='GenerateEateriesListQueue.import'),
		Queue('ScrapeEachEateryQueue', Exchange('default', delivery_mode=2),  routing_key='ScrapeEachEateryQueue.import'),
		Queue('MapListToTaskQueue', Exchange('default', delivery_mode=2),  routing_key='MapListToTaskQueue.import'),
		Queue('GoogleNPicsQueue', Exchange('default', delivery_mode=2),  routing_key='GoogleNPicsQueue.import'),

                )

CELERY_ROUTES = {
		'ZomatoScrapeTasks.StartScrapeChain': {
				'queue': 'StartScrapeChainQueue',
				'routing_key': 'StartScrapeChainQueue.import',
					},
		'ZomatoScrapeTasks.GenerateEateriesList': {
				'queue': 'GenerateEateriesListQueue',
				'routing_key': 'GenerateEateriesListQueue.import',
				},

		'ZomatoScrapeTasks.ScrapeEachEatery': {
				'queue': 'ScrapeEachEateryQueue',
				'routing_key': 'ScrapeEachEateryQueue.import',
							        },
		'ZomatoScrapeTasks.MapListToTask': {
				'queue': 'MapListToTaskQueue',
				'routing_key': 'MapListToTaskQueue.import',
							        },
		'ZomatoScrapeTasks.GoogleNPicsTask': {
				'queue': 'GoogleNPicsQueue',
				'routing_key': 'GoogleNPicsQueue.import',
							        },
			}

#BROKER_HOST = ''
#BROKER_PORT = ''
#BROKER_USER = ''
#BROKER_PASSWORD = ''
#BROKER_POOL_LIMIT = 20

#Celery result backend settings, We are using monngoodb to store the results after running the tasks through celery
CELERY_RESULT_BACKEND = 'mongodb'

# mongodb://192.168.1.100:30000/ if the mongodb is hosted on another sevrer or for that matter running on different port or on different url on 
#the same server

CELERY_MONGODB_BACKEND_SETTINGS = {
		'host': 'localhost',
		'port': 27017,
		'database': 'celery',
#		'user': '',
#		'password': '',
		'taskmeta_collection': 'celery_taskmeta',
			}



CELERYD_PREFETCH_MULTIPLIER= 1
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['application/json']
CELERY_ENABLE_UTC = True
CELERYD_CONCURRENCY = 20
#CELERYD_LOG_FILE="%s/celery.log"%os.path.dirname(os.path.abspath(__file__))
CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_PERSISTENT = True #Keeps the result even after broker restart
#CELERYD_POOL = 'gevent'



