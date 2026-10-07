import 'whatwg-fetch';
import '@selectize/selectize';
import FetchUtil from '../utils/fetchUtil';
import Exception from '../exceptions/exception';
import AttendanceException from '../exceptions/attendanceException';
import AdHocException from '../exceptions/adhocException';
import FetchException from '../exceptions/fetchException';

export default class AdHoc {
  constructor(element) {
    this.element = element;
    this.dataSrc = element.dataset.src;
    this.followSelector = element.dataset.follow;
    this.parentId = element.dataset.parent;
    this.list = element.list;

    if (!this.followSelector) {
      throw new Exception(AdHocException.NO_FOLLOW_ATTRIBUTE);
    } else if (!this.parentId) {
      throw new Exception(AdHocException.NO_PARENT_ATTRIBUTE);
    }

    if (this.dataSrc) {
      fetch('/attendance/' + this.dataSrc, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      })
        .then(FetchUtil.checkResponse)
        .then(FetchUtil.parseJSON)
        .then(response => {
          response.adhocs.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            element.list.appendChild(option);
          });
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
    const parentElem = document.getElementById(this.parentId);

    document.querySelectorAll(this.followSelector).forEach(input => {
      if (input.value === 'Ad-Hoc') {
        parentElem.style.display = 'block';
      }

      input.addEventListener('change', event => {
        if (event.target.value === 'Ad-Hoc') {
          parentElem.style.display = 'block';
        } else {
          parentElem.style.display = 'none';
        }
      });
    });
  }
}
