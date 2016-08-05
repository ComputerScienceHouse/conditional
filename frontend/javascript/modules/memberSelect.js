/* global fetch */
import "whatwg-fetch";
import "selectize";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import AttendanceException from "../exceptions/attendanceException";
import FetchException from "../exceptions/fetchException";

export default class MemberSelect {
  constructor(element) {
    this.element = element;
    this.dataSrc = element.dataset.src;

    if (typeof this.dataSrc === "undefined" ||
        this.dataSrc === "" ||
        this.dataSrc === null) {
      throw new Exception(AttendanceException.NO_SRC_ATTRIBUTE);
    } else {
      fetch('/attendance/' + this.dataSrc, {
        method: 'GET',
        credentials: 'same-origin'
      })
        .then(FetchUtil.checkResponse)
        .then(FetchUtil.parseJSON)
        .then(response => {
          this.members = response.members;
          this.render();
        })
        .catch(error => {
          throw new Exception(FetchException.REQUEST_FAILED, error);
        });
    }
  }

  render() {
    window.$(this.element).selectize({
      persist: false,
      openOnFocus: false,
      closeAfterSelect: true,
      plugins: ['remove_button'],
      valueField: 'value',
      labelField: 'display',
      searchField: 'display',
      selectOnTab: true,
      options: this.members
    });
  }
}
