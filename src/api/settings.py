import os
import ecs_logging
from pathlib import Path
from datetime import timedelta
import mongoengine
from pymongo import ReadPreference
from api import iva

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

# create logs folder
logs_folder = '../logs'
if not os.path.isdir(logs_folder):
    os.makedirs(logs_folder)

# mongo logging
iva.register_mongo_monitor()

# CLIENT ID: change for each client
CLIENT_ID = 2

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('JWT_SECRET')
API_KEY = os.getenv('API_KEY_WEB_SERVICE')
API_KEY_VINBUS = os.getenv('API_KEY_VINBUS')
API_KEY_MK = os.getenv('API_KEY_MK')
SITE_CODE = os.getenv('SITE_CODE')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = iva.bool_env(os.getenv('DEBUG'))

ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    '10.124.66.153',
    '10.124.66.173',
    '*'
]

# ALLOWED_HOSTS = [
#     '*'
# ]

# MINIO
MINIO = iva.get_minio_config_from_env()
ROOT_FOLDER_CAMERA = 'camera'
ROOT_FOLDER_DOSSIER = 'dossier'
ROOT_FOLDER_UPLOAD = 'uploads'

WATCHLIST_SERVICE = os.getenv('WATCHLIST_SERVICE')
API_KEY_WATCHLIST_SERVICE = os.getenv('API_KEY_WATCHLIST_SERVICE')

KAFKA_BOOTSTRAP_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVER')
# alert topic: new format
KAFKA_TOPIC_ALERT = os.getenv('KAFKA_TOPIC_ALERT') or 'iva.alert'
KAFKA_TOPIC_EVENT_LICENSE_PLATE = os.getenv('KAFKA_TOPIC_EVENT_LICENSE_PLATE') or 'iva.coreapi.event.licenseplate'

# face dossier
API_GET_FACE_DOSSIER = WATCHLIST_SERVICE + '/api/face/dossiers/'
API_GET_BULK_FACE_DOSSIERS = WATCHLIST_SERVICE + '/api/face/dossiers/bulk-get'
API_GET_FACE_DOSSIER_ITEM = WATCHLIST_SERVICE + '/api/face/dossier-items/'
API_GET_BULK_FACE_WATCHLISTS = WATCHLIST_SERVICE + '/api/face/watchlists/bulk-get'

# human dossier
API_GET_HUMAN_DOSSIER = WATCHLIST_SERVICE + '/api/human/dossiers/'
API_GET_BULK_HUMAN_DOSSIERS = WATCHLIST_SERVICE + '/api/human/dossiers/bulk-get'
API_GET_HUMAN_DOSSIER_ITEM = WATCHLIST_SERVICE + '/api/human/dossier-items/'
API_GET_BULK_HUMAN_WATCHLISTS = WATCHLIST_SERVICE + '/api/human/watchlists/bulk-get'

# plate
API_GET_PLATE = WATCHLIST_SERVICE + '/api/plate/plates/'
API_GET_BULK_PLATES = WATCHLIST_SERVICE + '/api/plate/plates/bulk-get'
API_GET_BULK_PLATE_WATCHLISTS = WATCHLIST_SERVICE + '/api/plate/watchlists/bulk-get'

# vehicle dossier
API_GET_VEHICLE_DOSSIER = WATCHLIST_SERVICE + '/api/vehicle/dossiers/'
API_GET_BULK_VEHICLE_DOSSIERS = WATCHLIST_SERVICE + '/api/vehicle/dossiers/bulk-get'
API_GET_VEHICLE_DOSSIER_ITEM = WATCHLIST_SERVICE + '/api/vehicle/dossier-items/'
API_GET_BULK_VEHICLE_WATCHLISTS = WATCHLIST_SERVICE + '/api/vehicle/watchlists/bulk-get'


# Application definition
INSTALLED_APPS = [
    # addons
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'crispy_forms',
    'django_filters',
    # django Prometheus exporter
    'django_prometheus',

    # core
    'apps.core',

    #khanhvan
    'apps.khanhvan',

    #chatbot
    'apps.chatbot',

]
# for specify column of django-safedelete model: SAFE_DELETE_FIELD_NAME = 'deleted_at'

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # django Prometheus exporter
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # django Prometheus exporter
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

FILE_UPLOAD_HANDLERS = ["common.minio_file_handler.MinioUploadedFileHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler"]

# Database
# With mysql cluster, using mysql router host
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.getenv('MYSQL_DB_HOST'),
        'NAME': os.getenv('MYSQL_DB_NAME'),
        'USER': os.getenv('MYSQL_DB_USER'),
        'PASSWORD': os.getenv('MYSQL_DB_PASSWORD'),
        'PORT': os.getenv('MYSQL_DB_PORT'),
        # 'POOL_OPTIONS': {
        #     'POOL_SIZE': 5,
        #     'MAX_OVERFLOW': 5
        # },
        'TIME_ZONE': 'Asia/Saigon',
        "OPTIONS": {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            "charset": "utf8mb4",
            "init_command": "SET GLOBAL max_connections = 1024",
        },
        'TEST': {
            'NAME': 'test_' + os.getenv('MYSQL_DB_NAME')
        }
    }
}
DJANGO_MYSQL_REWRITE_QUERIES = True

# mongodb
MONGODB_READ_PREFERENCE_MAPS = {
    'primary': ReadPreference.PRIMARY,
    'primaryPreferred': ReadPreference.PRIMARY_PREFERRED,
    'secondary': ReadPreference.SECONDARY,
    'secondaryPreferred': ReadPreference.SECONDARY_PREFERRED,
}
read_preference = MONGODB_READ_PREFERENCE_MAPS.get(os.getenv('MONGODB_READ_PREFERENCE'),
                                                   ReadPreference.PRIMARY_PREFERRED)
# if MONGO_DB_HOST is a full connection string, it will overwrite other params (port, db, pass, auth source)
mongoengine.connect(host=os.getenv('MONGO_DB_HOST'),
                    port=int(os.getenv('MONGO_DB_PORT')),
                    db=os.getenv('MONGO_DB_NAME'), username=os.getenv('MONGO_DB_USER'),
                    password=os.getenv('MONGO_DB_PASSWORD'),
                    authentication_source='admin',
                    read_preference=read_preference)

# django cache
if os.getenv('REDIS_SENTINEL'):
    # redis replicaset with sentinel
    DJANGO_REDIS_CONNECTION_FACTORY = 'django_redis.pool.SentinelConnectionFactory'
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            # db0 contains alert:latest:[user_id]
            'LOCATION': 'redis://' + ':' + os.getenv('REDIS_AUTH') + '@' + os.getenv('REDIS_MASTER_GROUP_NAME') + '/0',
            'OPTIONS': {
                "CLIENT_CLASS": "django_redis.client.SentinelClient",
                "SENTINELS": iva.parse_redis_sentinel_config(os.getenv('REDIS_SENTINEL')),
                "SENTINEL_KWARGS": {},
                "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
            }
        },
        "local": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "web-service-cache",
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://' + ':' + os.getenv('REDIS_AUTH') + '@' + os.getenv('REDIS_HOST') + ':' +
                        os.getenv('REDIS_PORT') + '/',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        },
        "local": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "web-service-cache",
        }
    }

# Logstash
logstash_host = os.getenv('LOGSTASH_HOST')
logstash_port = os.getenv('LOGSTASH_PORT')

DEFAULT_LOG_HANDLER_NAME = 'logging.handlers.TimedRotatingFileHandler'
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '{levelname:<5} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'ecs_formatter': {
            '()': ecs_logging.StdlibFormatter,
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'db_file_log': {
            'level': 'DEBUG',
            'class': DEFAULT_LOG_HANDLER_NAME,
            'filename': '../logs/query.log',
            'when': 'D',  # this specifies the interval
            'backupCount': 10,  # how many backup file to keep, 10 days
            'formatter': 'verbose'
        },
        'mongo_file_log': {
            'level': 'DEBUG',
            'class': DEFAULT_LOG_HANDLER_NAME,
            'filename': '../logs/mongo.log',
            'when': 'D',  # this specifies the interval
            'backupCount': 10,  # how many backup file to keep, 10 days
            'formatter': 'verbose'
        },
        'file_info': {
            'level': 'INFO',
            'class': DEFAULT_LOG_HANDLER_NAME,
            'filename': '../logs/debug.log',
            'when': 'D',  # this specifies the interval
            'backupCount': 10,  # how many backup file to keep, 10 days
            'formatter': 'ecs_formatter',
        },
        'file_error': {
            'level': 'ERROR',
            'class': DEFAULT_LOG_HANDLER_NAME,
            'filename': '../logs/error.log',
            'when': 'D',  # this specifies the interval
            'backupCount': 10,  # how many backup file to keep, 10 days
            'formatter': 'ecs_formatter',
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': logstash_host,  # IP/name of our Logstash EC2 instance
            'port': logstash_port,
            'version': 1,
            'message_type': 'logstash',
            'fqdn': True,
            'tags': ['iva'],
        }
    },
    'loggers': {
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_file_log'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'mongo': {
            'handlers': ['mongo_file_log'],
            'propagate': False,
            'level': 'DEBUG',
        },
    }
}

APP_ORDER = [
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'apps.user_management.auth.token_authentication.CustomJWTAuthentication',
    # ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'apps.user_management.auth.permissions.IsAuthenticatedByTokenOrKey',
    # ],
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'EXCEPTION_HANDLER': 'drf_standardized_errors.handler.exception_handler',
}

DRF_STANDARDIZED_ERRORS = {
    "EXCEPTION_FORMATTER_CLASS": "common.my_exception_handler.MyExceptionFormatter",
    "EXCEPTION_HANDLER_CLASS": "common.my_exception_handler.MyExceptionHandler"
}

# === 04/04/2025 ===
CORS_ORIGIN_ALLOW_ALL = True

# CORS_ALLOW_CREDENTIALS = True
# CORS_EXPOSE_HEADERS = ['Content-Disposition']
# CORS_ALLOWED_ORIGINS = []
#
# list_hosts = iva.parse_cors_allowed_string()
# if list_hosts:
#     CORS_ORIGIN_ALLOW_ALL = True
#     CORS_ALLOW_CREDENTIALS = True
#     CORS_ALLOWED_ORIGINS = list_hosts

# AUTH_USER_MODEL = "user_management.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "JTI_CLAIM": "jti",
    # "TOKEN_OBTAIN_SERIALIZER": "apps.user_management.serializers.CustomTokenObtainPairSerializer",
    # "TOKEN_REFRESH_SERIALIZER": "apps.user_management.serializers.CustomTokenRefreshSerializer",
    # "TOKEN_VERIFY_SERIALIZER": "apps.user_management.serializers.CustomTokenVerifySerializer",
    # "TOKEN_BLACKLIST_SERIALIZER": "apps.user_management.serializers.CustomTokenBlacklistSerializer",
    # "USER_AUTHENTICATION_RULE": "apps.user_management.models.user.default_user_authentication_rule",
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Saigon'  # or UTC
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Swagger settings
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

# Issue with package django-prometheus when custom AUTH_USER_MODEL
# https://github.com/korfuri/django-prometheus/issues/303
PROMETHEUS_EXPORT_MIGRATIONS = False

SERVICE_NAME = os.getenv('SERVICE_NAME', 'web-service')
TELEGRAF_HOST = os.getenv('TELEGRAF_HOST')
TELEGRAF_PORT = int(os.getenv('TELEGRAF_PORT', 0))

