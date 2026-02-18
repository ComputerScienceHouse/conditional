import os

wsgi_app = 'conditional:app'
bind = f'0.0.0.0:{os.getenv('PORT', 8080)}'
workers = os.getenv('CONDITIONAL_WORKERS', 1)
accesslog = '-'
timeout = 256
