import FetchUtil from '../utils/fetchUtil';
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import sweetAlert from "../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js"; // eslint-disable-line max-len

export default class NewYear {
  constructor(link) {
    this.link = link;
    this.step = this.link.dataset.step;
    this.uid = this.link.dataset.uid;

    this.endpoints = {
      housing: '/housing',
      active: '/manage/active',
      current: '/manage/current/'
    };

    this.render();
  }
  render() {
    this.link.addEventListener('click', e => {
      e.preventDefault();

      if (this.step === "welcome") {
        $('#new-welcome').fadeOut(() => {
          $("#new-clear").fadeIn();
        });
      } else if (this.step === "clear") {
        FetchUtil.fetchWithWarning(this.endpoints.active, {
          method: 'DELETE',
          warningText: "This will clear active members and room assignments!",
          successText: "Data successfully cleared."}, () => {
            fetch(this.endpoints.housing, {
              method: 'DELETE',
              credentials: "same-origin"
            })
            .then($('#new-clear').fadeOut(() => {
              $("#new-current").fadeIn();
            })
            ).catch(error => {
              sweetAlert("Uh oh...", "We're having trouble submitting that " +
                          "action right now. Please try again later.", "error");
              throw new Exception(FetchException.REQUEST_FAILED, error);
            });
          });
      } else if (this.uid) {
        if ($('#rem-' + this.uid).is(":visible")) {
          fetch(this.endpoints.current + this.uid, {
            method: 'DELETE',
            credentials: "same-origin"
          }).then(() => {
            $('#rem-' + this.uid).hide();
            $('#add-' + this.uid).show();
            var userRow = $('#row-' + this.uid)[0];
            userRow.style.setProperty("text-decoration", "line-through");
          }).catch(error => {
            sweetAlert("Uh oh...", "We're having trouble submitting that " +
                        "action right now. Please try again later.", "error");
            throw new Exception(FetchException.REQUEST_FAILED, error);
          });
        } else {
          fetch(this.endpoints.current + this.uid, {
            method: 'POST',
            credentials: "same-origin"
          }).then(() => {
            $('#add-' + this.uid).hide();
            $('#rem-' + this.uid).show();
            var lineRow = $('#row-' + this.uid)[0];
            lineRow.style.setProperty("text-decoration", "none");
          }).catch(error => {
            sweetAlert("Uh oh...", "We're having trouble submitting that " +
                        "action right now. Please try again later.", "error");
            throw new Exception(FetchException.REQUEST_FAILED, error);
          });
        }
      } else if (this.step === "current") {
        $('#new-current').fadeOut(function() {
          $("#new-housing").fadeIn();
        });
      }
    });
  }
}
