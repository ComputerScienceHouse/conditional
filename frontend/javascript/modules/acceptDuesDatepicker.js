/* global $ */
import "bootstrap-material-datetimepicker";
import "whatwg-fetch";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import sweetAlert from "bootstrap-sweetalert/dev/sweetalert.es6.js";

export default class DatePicker {
  constructor(input) {
    this.input = input;
    this.endpoint = '/manage/accept_dues_until';
    this.setting = input.dataset.setting;
    this.render();
  }

  render() {
    $(this.input).bootstrapMaterialDatePicker({
      weekStart: 0,
      time: false
    });

    document.getElementsByClassName('dtp-btn-ok')[0].addEventListener('click',
    () => {
      this._updateSetting();
    });
  }

  _updateSetting() {
    console.log("Update dues until: " + this.input.value);
    let payload = {};
    payload[this.setting] = this.input.value;

    fetch(this.endpoint, {
      method: 'PUT',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    })
      .then(FetchUtil.checkStatus)
      .then(FetchUtil.parseJSON)
      .then(response => {
        if (!response.hasOwnProperty('success') || !response.success) {
          sweetAlert("Uh oh...", "We're having trouble submitting this " +
              "form right now. Please try again later.", "error");
          throw new Exception(FetchException.REQUEST_FAILED, response);
        }
      })
      .catch(error => {
        sweetAlert("Uh oh...", "We're having trouble submitting this " +
            "form right now. Please try again later.", "error");
        throw new Exception(FetchException.REQUEST_FAILED, error);
      });
  }
}
