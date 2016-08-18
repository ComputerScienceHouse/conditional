/* global fetch */
import "whatwg-fetch";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import sweetAlert from "../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js"; // eslint-disable-line max-len

export default class FetchUtil {
  static checkStatus(response) {
    if (response.status < 200 || response.status > 300) {
      throw new Exception(
        FetchException.REQUEST_FAILED,
        "received response code " + response.status
      );
    }

    return response;
  }

  static parseJSON(response) {
    return response.json();
  }

  static postWithWarning(endpoint, payload, settings, callback) {
    sweetAlert({
      title: "Are you sure?",
      text: settings.warningText,
      type: "warning",
      showCancelButton: true,
      closeOnConfirm: false,
      showLoaderOnConfirm: true
    }, () => {
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
        .then(FetchUtil.checkResponse)
        .then(FetchUtil.parseJSON)
        .then(response => {
          if (response.hasOwnProperty('success') && response.success === true) {
            sweetAlert({
              title: "Success!",
              text: settings.successText,
              type: "success",
              confirmButtonText: "OK"
            }, () => {
              if (typeof callback === "function") {
                callback();
              } else {
                window.location.reload();
              }
            });
          } else {
            sweetAlert("Uh oh...", "We're having trouble submitting this form" +
                        "right now. Please try again later.", "error");
            throw new Exception(FetchException.REQUEST_FAILED, response);
          }
        })
        .catch(error => {
          sweetAlert("Uh oh...", "We're having trouble submitting this form" +
                      "right now. Please try again later.", "error");
          throw new Exception(FetchException.REQUEST_FAILED, error);
        });
    });
  }

  static getWithWarning(endpoint, settings, callback) {
    sweetAlert({
      title: "Are you sure?",
      text: settings.warningText,
      type: "warning",
      showCancelButton: true,
      closeOnConfirm: false,
      showLoaderOnConfirm: true
    }, () => {
      fetch(endpoint, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
          .then(FetchUtil.checkResponse)
          .then(FetchUtil.parseJSON)
          .then(response => {
            if (response.hasOwnProperty('success') &&
                response.success === true) {
              sweetAlert({
                title: "Success!",
                text: settings.successText,
                type: "success",
                confirmButtonText: "OK"
              }, () => {
                if (typeof callback === "function") {
                  callback();
                } else {
                  window.location.reload();
                }
              });
            } else {
              sweetAlert("Uh oh...", "We're having trouble submitting " +
                  "this form right now. Please try again later.", "error");
              throw new Exception(FetchException.REQUEST_FAILED, response);
            }
          })
          .catch(error => {
            sweetAlert("Uh oh...", "We're having trouble submitting this " +
                "form right now. Please try again later.", "error");
            throw new Exception(FetchException.REQUEST_FAILED, error);
          });
    });
  }
}
