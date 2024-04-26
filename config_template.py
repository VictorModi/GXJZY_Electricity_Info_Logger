from pytz import timezone
from datetime import timedelta

# School site URL
BASE_URL: str = 'http://cw.gxjzy.com:8081'

# Timezone
TIMEZONE: timezone = timezone('Asia/Shanghai')

# Configuration for time interval
# TIME_INTERVAL controls the interval for fetching electricity information from the website.
# Setting the interval too short may cause excessive requests and strain on the website's servers.
# It is recommended not to set the interval too short to avoid potential issues.
TIME_INTERVAL = timedelta(minutes=10)  # Adjust this time interval as needed

# Student ID or ID card number
SID: str = '2023040****'

# IMPORTANT: Storing plain-text passwords is insecure and should be avoided whenever possible.
# This is for demonstration purposes only. In production, consider using secure methods like
# environment variables or encrypted storage.
PASSWORD: str = '******'

# CUST_ID represents the dormitory ID, not the dormitory number.
# The specific value depends on the response returned by the school's website.
CUST_ID: str = "****"

# Whether to log dormitory address ID information
LOGGING_ADDR = False

# MongoDB configuration
DATABASE_URL: str = "mongodb://localhost:27017"  # MongoDB connection URL
DATABASE_NAME: str = "electricity"  # Name of the database
DATABASE_COLLECTION: str = "log"  # Name of the collection for logging

# Access token for authentication (optional, API is unauthenticated if not provided)
# WARNING: It's not recommended to leave ACCESS_TOKEN unset for production environments.
# API access may be unauthenticated if ACCESS_TOKEN is not provided.
ACCESS_TOKEN: str = "ACCESS_TOKEN"

# Configuration for FastAPI (WebAPI) port
FAST_API_PORT = 8088  # Change this port number if necessary

LOGGING_CONFIG: dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'uvicorn': {
            'handlers': [
                'default',
            ],
            'level': 'INFO',
        },
        'uvicorn.error': {
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': [
                'access',
            ],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
