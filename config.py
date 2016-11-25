from os import environ

# Flask Settings
DEBUG = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Flask WTF Forms settings
WTF_CSRF_ENABLED = True

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Flask Mail Settings
# MAIL_SERVER = 'mail.evans.gb.net'
# MAIL_PORT = 110
# MAIL_USERNAME = environ.get('MAIL_USERNAME')
# MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'jack@example.com'
