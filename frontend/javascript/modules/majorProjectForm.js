import FetchUtil from "../utils/fetchUtil";

export default class MajorProjectForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/major_project/submit';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this._submitForm(e));
  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      projectName: this.form.querySelector('input[name=name]').value,
      projectDescription:
        this.form.querySelector('textarea[name=description]').value
    };

    FetchUtil.postWithWarning(this.endpoint, payload, {
      warningText: "You will not be able to edit your " +
        "project once it has been submitted.",
      successText: "Your project has been submitted."
    });
  }
}
