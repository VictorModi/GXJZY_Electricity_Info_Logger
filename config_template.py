from datetime import timedelta

# School site URL
BASE_URL: str = 'http://cw.gxjzy.com:8081'

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

# MySQL server address
MYSQL_HOST: str = "127.0.0.1"
# MySQL server port
MYSQL_PORT: int = 3306
# MySQL username
MYSQL_USER: str = "root"
# MySQL password
MYSQL_PASSWORD: str = ""
# MySQL database name
MYSQL_DATABASE: str = "electricity"
# MySQL table name
MYSQL_TABLE_NAME: str = "log"
# MySQL's character set
MYSQL_CHARSET: str = "utf8mb4"

MAX_RETRIES: int = 3
RETRY_DELAY: int = 5
# Access token for authentication (optional, API is unauthenticated if not provided)
# WARNING: It's not recommended to leave ACCESS_TOKEN unset for production environments.
# API access may be unauthenticated if ACCESS_TOKEN is not provided.
ACCESS_TOKEN: str = "ACCESS_TOKEN"

# Configuration for FastAPI (WebAPI) port
PORT = 8088  # Change this port number if necessary

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
