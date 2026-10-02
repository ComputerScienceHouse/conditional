// Install Sentry to send errors to Sentry
import * as Sentry from '@sentry/browser';

// Capture unhandled exceptions in promises
window.addEventListener('unhandledrejection', err => {
  Sentry.captureException(err.reason);
});

// Load the rest of the modules
import "jquery";
import "bootstrap";
import "./modules";

import 'csh-material-bootstrap/color-modes.js';

import "masonry-layout";

// Load fonts
import "bootstrap-icons/font/fonts/bootstrap-icons.woff"
import "bootstrap-icons/font/fonts/bootstrap-icons.woff2"

// Load styles
import "../stylesheets/app.scss"
import "../stylesheets/presentations.scss"
