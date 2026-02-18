import os

bind = f'0.0.0.0:{os.getenv('PORT')}'
workers = os.getenv('CONDITIONAL_WORKERS', 1)
accesslog = '-'
timeout = 256
