/* global $ */
import "whatwg-fetch";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import Swal from "sweetalert2";
import { Datepicker } from "vanillajs-datepicker";

export default class DatePicker {
  constructor(input) {
    this.input = input;
    this.selectedDate = new Date(Datepicker.parseDate(this.input.value, 'yyyy-mm-dd'));
    this.endpoint = '/manage/accept_dues_until';
    this.setting = input.dataset.setting;
    this.render();
  }

  render() {
    new Datepicker(this.input, {
      buttonClass: 'btn',
      todayButton: true,
      format: 'yyyy-mm-dd',
      autohide: true
    })

    this.input.addEventListener("hide", (event) => {
      if (event.detail.date.getTime() != this.selectedDate.getTime()) {
        this._updateSetting();
      }
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
          Swal.fire("Uh oh...", "We're having trouble submitting this " +
              "form right now. Please try again later.", "error");
          throw new Exception(FetchException.REQUEST_FAILED, response);
        }

        this.selectedDate = this.input.datepicker.getDate();
      })
      .catch(error => {
        Swal.fire("Uh oh...", "We're having trouble submitting this " +
            "form right now. Please try again later.", "error");
        throw new Exception(FetchException.REQUEST_FAILED, error);
      });
  }
}
