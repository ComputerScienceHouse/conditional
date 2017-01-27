import Raven from 'raven-js';

export default class ErrorReport {
    constructor(btn) {
        this.btn = btn;
        this.eventId = this.btn.dataset.event;
        this.render();
    }
    
    render() {
        this.btn.addEventListener('click', () => this._invokeRavenModal());
    }
    
    _invokeRavenModal() {
        Raven.showReportDialog({
            eventId: this.eventId
        });
    }
}
