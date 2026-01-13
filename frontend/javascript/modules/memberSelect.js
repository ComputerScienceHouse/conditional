/* global fetch */
import "whatwg-fetch";
import "@selectize/selectize";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import AttendanceException from "../exceptions/attendanceException";
import FetchException from "../exceptions/fetchException";

export default class MemberSelect {
  constructor(element) {
    this.element = element;
    this.dataSrc = element.dataset.src;

    if (this.dataSrc) {
      fetch('/attendance/' + this.dataSrc, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
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
    } else {
      throw new Exception(AttendanceException.NO_SRC_ATTRIBUTE);
    }
  }

  render() {
    $(this.element).selectize({
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
