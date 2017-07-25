import FetchUtil from "../utils/fetchUtil";

export default class coopSubmitForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/co_op/submit';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this._submitForm(e));
  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      semester: this.form.querySelector('input[name=semester]:checked').value
    };

    FetchUtil.postWithWarning(this.endpoint, payload, {
      warningText: "You will not be able to edit your " +
        "submission once it is submitted!",
      successText: "Your co-op has been submitted."
    });
  }
}
