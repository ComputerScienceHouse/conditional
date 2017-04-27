// Install Raven to send errors to Sentry
import Raven from 'raven-js';
Raven
    .config('https://151ecfab1a8242009012d45a19064cfd@sentry.io/133175')
    .install();

// Capture unhandled exceptions in promises
window.addEventListener('unhandledrejection', err => {
  Raven.captureException(err.reason);
});

// Load the rest of the modules
import "jquery";
import "bootstrap";
import "./modules";
