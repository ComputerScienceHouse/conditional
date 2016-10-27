import _ from "lodash";
import FetchUtil from "../utils/fetchUtil";

export default class IntroductoryProjectForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/manage/intro_project';

    this.render();
  }

  render() {
    // Prevent the form from submitting if the user hits the enter key
    ['keyup', 'keypress'].forEach(keyevent =>
      this.form.addEventListener(keyevent, event => {
        let keyCode = event.keyCode || event.which;
        if (keyCode === 13) {
          event.preventDefault();
          return false;
        }
      }, true));

    this.form.querySelectorAll('tbody > tr .btn-group').forEach(control => {
      control.querySelectorAll('[data-option]').forEach(option => {
        option.addEventListener('click', e => {
          e.preventDefault();

          let toggle = control.querySelector('.dropdown-toggle');

          ["btn-success", "btn-danger", "btn-warning"]
            .forEach(classToRemove =>
              toggle.classList.remove(classToRemove));

          const caret = document.createElement('span');
          caret.classList.add('caret');
          toggle.text = option.dataset.option + " ";
          toggle.appendChild(caret);
          toggle.dataset.selected = option.dataset.option;

          if (option.dataset.option === "Passed") {
            toggle.classList.add("btn-success");
          } else if (option.dataset.option === "Failed") {
            toggle.classList.add("btn-danger");
          } else {
            toggle.classList.add("btn-warning");
          }
        });
      });
    });

    // Form submit handler
    this.form.querySelectorAll("input[type=submit]").forEach(submitBtn => {
      submitBtn.addEventListener("click", e => {
        e.preventDefault();

        let payload = [];

        this.form.querySelectorAll("tbody > tr").forEach(freshman => {
          const uid = freshman.dataset.uid;
          const status = freshman.querySelector('.dropdown-toggle')
            .dataset.selected;

          // Quick sanity check
          if (!_.isNil(uid) && !_.isNil(status) &&
            (status === "Passed" || status === "Pending" ||
            status === "Failed")) {
            payload.push({
              uid: uid,
              status: status
            });
          }
        });

        FetchUtil.postWithWarning(this.endpoint, payload, {
          warningText: "Are you sure you want to update the introductory " +
          "project results?",
          successText: "Introductory project results have been submitted."
        });
      });
    });
  }
}
