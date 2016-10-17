import FetchUtil from "../utils/fetchUtil";
import MemberUtil from "../utils/memberUtil";

export default class AttendanceForm {
  constructor(form) {
    this.form = form;

    this.fields = {
      timestamp: this.form.elements.date,
      attendees: this.form.elements.attendees
    };

    this.endpoint = '';

    if (this.form.dataset.type === "committee") {
      this.endpoint = '/attendance/submit/cm';
      this.fields.committee = this.form.elements.committee;
    } else if (this.form.dataset.type === "seminar") {
      this.endpoint = '/attendance/submit/ts';
      this.fields.name = this.form.elements.name;
    }

    this.render();
  }

  render() {
    // Prevent the form from submitting if the user hits the enter key
    ['keyup', 'keypress'].forEach(keyevent =>
      this.form.addEventListener(keyevent, event => {
        let keyCode = event.keyCode || event.which;
        if (keyCode === 13) {
          event.preventDefault();
          return false;
        }
      }, true));

    // Form submit handler
    this.form.querySelectorAll("input[type=submit]").forEach(submitBtn => {
      submitBtn.addEventListener("click", e => {
        e.preventDefault();
        let payload = {};

        Object.keys(this.fields).forEach(field => {
          if (field === "attendees") {
            let membersSplit = MemberUtil.splitFreshmenUpperclassmen(
              this.fields[field].value.split(',')
            );
            payload.freshmen = membersSplit.freshmen;
            payload.members = membersSplit.upperclassmen;
          } else {
            payload[field] = this.fields[field].value;
          }
        });

        FetchUtil.postWithWarning(this.endpoint, payload, {
          warningText: "You will not be able to edit this event once " +
                        "attendance has been recorded.",
          successText: "Attendance has been submitted."
        });
      });
    });
  }
}
