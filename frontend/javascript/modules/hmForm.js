import _ from "lodash";
import FetchUtil from "../utils/fetchUtil";

export default class HouseMeetingForm {
  constructor(form) {
    this.form = form;

    this.endpoint = '/attendance/submit/hm';
    this.fields = {
      timestamp: this.form.elements.date
    };

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
          payload[field] = this.fields[field].value;
        });

        let freshmen = [];
        let upperclassmen = [];

        this.form.querySelectorAll("input[type=checkbox]").forEach(checkbox => {
          const uid = checkbox.name;
          const status = checkbox.checked ? "Attended" : "Absent";

          if (_.isNaN(uid)) {
            upperclassmen.push({
              uid: uid,
              status: status
            });
          } else {
            freshmen.push({
              id: uid,
              status: status
            });
          }
        });

        payload.freshmen = freshmen;
        payload.members = upperclassmen;

        FetchUtil.postWithWarning(this.endpoint, payload, {
          warningText: "You will not be able to unmark a member as present" +
                        "once attendance has been recorded.",
          successText: "Attendance has been submitted."
        });
      });
    });
  }
}
