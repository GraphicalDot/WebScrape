from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/0'

# CELERY_IMPORTS = ("new_tasks")


CELERY_QUEUES = (
		Queue('StartScrapeChainQueue', Exchange('default', delivery_mode= 2),  routing_key='StartScrapeChainQueue.import'),
		Queue('GenerateEateriesListQueue', Exchange('default', delivery_mode= 2),  routing_key='GenerateEateriesListQueue.import'),
		Queue('ScrapeEachEateryQueue', Exchange('default', delivery_mode=2),  routing_key='ScrapeEachEateryQueue.import'),
		Queue('MapListToTaskQueue', Exchange('default', delivery_mode=2),  routing_key='MapListToTaskQueue.import'),
                )


# Queue('GoogleNPicsQueue', Exchange('default', delivery_mode=2),  routing_key='GoogleNPicsQueue.import'),


CELERY_ROUTES = {
		'zomato_tasks.start_scraping': {
				'queue': 'StartScrapeChainQueue',
				'routing_key': 'StartScrapeChainQueue.import',
					},
		'zomato_tasks.get_eateries_list': {
				'queue': 'GenerateEateriesListQueue',
				'routing_key': 'GenerateEateriesListQueue.import',
				},

		'zomato_tasks.get_eatery_info': {
				'queue': 'ScrapeEachEateryQueue',
				'routing_key': 'ScrapeEachEateryQueue.import',
							        },
		'zomato_tasks.execute_all_eateries': {
				'queue': 'MapListToTaskQueue',
				'routing_key': 'MapListToTaskQueue.import',
							        },
			}


# 'ZomatoScrapeTasks.google_n_pics_task': {
# 				'queue': 'GoogleNPicsQueue',
# 				'routing_key': 'GoogleNPicsQueue.import',
# 							        },

# mongodb://192.168.1.100:30000/ if the mongodb is hosted on another sevrer or for that matter running on different port or on different url on 
# the same server

CELERY_RESULT_BACKEND = 'mongodb'

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
CELERYD_CONCURRENCY = 10
# CELERYD_LOG_FILE="%s/celery.log"%os.path.dirname(os.path.abspath(__file__))
CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_PERSISTENT = True #Keeps the result even after broker restart
