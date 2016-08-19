/* global fetch */
import "whatwg-fetch";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import FetchUtil from "../utils/fetchUtil";
import sweetAlert from "../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js"; // eslint-disable-line max-len

export default class MajorProjectStatus {
  constructor(dropdown) {
    this.dropdown = dropdown;
    this.id = this.dropdown.dataset.id;
    this.endpoint = '/major_project/review';
    this.render();
  }

  render() {
    const options = this.dropdown.querySelectorAll('[data-option]');
    options.forEach(option => {
      option.addEventListener('click', e => this._changeStatus(e));
    });
  }

  _changeStatus(e) {
    e.preventDefault();

    let option = e.target.dataset.option;
    let payload = {
      id: this.id,
      status: option
    };

    fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
      .then(FetchUtil.checkStatus)
      .then(FetchUtil.parseJSON)
      .then(response => {
        if (response.hasOwnProperty('success') && response.success === true) {
          let toggle = this.dropdown.querySelector('.dropdown-toggle');
          ["btn-success", "btn-danger", "btn-warning"].forEach(classToRemove =>
            toggle.classList.remove(classToRemove));

          const caret = document.createElement('span');
          caret.classList.add('caret');
          toggle.text = option + " ";
          toggle.appendChild(caret);

          if (option === "Passed") {
            toggle.classList.add("btn-success");
          } else if (option === "Failed") {
            toggle.classList.add("btn-danger");
          } else {
            toggle.classList.add("btn-warning");
          }
        } else {
          sweetAlert("Uh oh...", "We're having trouble updating this project " +
            "right now. Please try again later.", "error");
          throw new Exception(FetchException.REQUEST_FAILED, response);
        }
      })
      .catch(error => {
        sweetAlert("Uh oh...", "We're having trouble updating this project " +
          "right now. Please try again later.", "error");
        throw new Exception(FetchException.REQUEST_FAILED, error);
      });
  }
}
