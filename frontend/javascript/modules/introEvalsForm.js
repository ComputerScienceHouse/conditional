import FetchUtil from "../utils/fetchUtil";

export default class IntroEvalsForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/intro_evals/submit';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this._submitForm(e));
  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      socialEvents:
        this.form.querySelector('textarea[name=social_events]').value,
      comments:
        this.form.querySelector('textarea[name=comments]').value
    };

    FetchUtil.post(this.endpoint, payload, {
      successText: "Your social events and comments have been updated."
    });
  }
}
