// Install Sentry to send errors to Sentry
import * as Sentry from '@sentry/browser';
Sentry.init(
  {
    dsn: 'https://151ecfab1a8242009012d45a19064cfd@sentry.io/133175'
  }
);

// Capture unhandled exceptions in promises
window.addEventListener('unhandledrejection', err => {
  Sentry.captureException(err.reason);
});

// Load the rest of the modules
import "jquery";
import "bootstrap";
import "./modules";

import "../stylesheets/app.scss"
import "../stylesheets/presentations.scss"
