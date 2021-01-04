import * as Sentry from '@sentry/browser';

export default class ErrorReport {
  constructor(btn) {
    this.btn = btn;
    this.eventId = this.btn.dataset.event;
    this.render();
  }

  render() {
    this.btn.addEventListener('click', () => this._invokeSentryModal());
  }

  _invokeSentryModal() {
    Sentry.showReportDialog({
      eventId: this.eventId
    });
  }
}
