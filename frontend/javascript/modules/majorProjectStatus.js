/* global fetch */
import "whatwg-fetch";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import FetchUtil from "../utils/fetchUtil";
import sweetAlert from "../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js"; // eslint-disable-line max-len

export default class MajorProjectStatus {
  constructor(control) {
    this.control = control;
    this.id = this.control.dataset.id;
    this.endpoint = '/major_project/review';
    this.deleteEndpoint = '/major_project/delete/' + this.id;
    this.render();
  }

  render() {
    if (this.control.tagName.toLowerCase() === "div") {
      // Evals director dropdown
      const options = this.control.querySelectorAll('[data-option]');
      options.forEach(option => {
        option.addEventListener('click', e => {
          e.preventDefault();
          this._changeStatus(e.target.dataset.option);
        });
      });
    } else {
      // Member self-delete button
      this.control.addEventListener('click',
          () => this._changeStatus('Delete'));
    }
  }

  _changeStatus(option) {
    if (option === "Delete") {
      FetchUtil.fetchWithWarning(this.deleteEndpoint, {
        method: 'DELETE',
        warningText: 'This action cannot be undone.',
        successText: 'Major project deleted.'
      }, () => {
        let dashboardContainer = this.control.closest(".mp-container");
        if (dashboardContainer) {
          // Dashboard button
          $(dashboardContainer).hide();
        } else {
          // Major projects page button
          $(this.control.closest(".panel")).fadeOut();
        }
      });
    } else {
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
        credentials: "same-origin",
        body: JSON.stringify(payload)
      })
          .then(FetchUtil.checkStatus)
          .then(FetchUtil.parseJSON)
          .then(response => {
            if (response.hasOwnProperty('success') &&
                response.success === true) {
              let toggle = this.control.querySelector('.dropdown-toggle');
              ["btn-success", "btn-danger", "btn-warning"]
                  .forEach(classToRemove =>
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
              sweetAlert("Uh oh...", "We're having trouble updating " +
                  "this project right now. Please try again later.", "error");
              throw new Exception(FetchException.REQUEST_FAILED, response);
            }
          })
          .catch(error => {
            sweetAlert("Uh oh...", "We're having trouble updating " +
                "this project right now. Please try again later.", "error");
            throw new Exception(FetchException.REQUEST_FAILED, error);
          });
    }
  }
}
