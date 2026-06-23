/* global $ */
import { Datepicker } from "vanillajs-datepicker";

export default class DatePicker {
  constructor(input) {
    this.input = input;

    this.render();
  }

  render() {
    new Datepicker(this.input, {
      buttonClass: 'btn',
      todayButton: true,
      format: 'yyyy-mm-dd',
      autohide: true
    })
  }
}
