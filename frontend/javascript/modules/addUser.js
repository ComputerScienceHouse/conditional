import FetchUtil from "../utils/fetchUtil";
import { SwalMixin } from "../utils/swal2Mixin";

export default class AddUser {
  constructor(form) {
    this.form = form;
    this.endpoint = '/manage/user';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this._submitForm(e));
  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      name: this.form.querySelector('input[name=name]').value,
      onfloor: this.form.querySelector('input[name=onFloor]').checked,
      roomNumber: this.form.querySelector('input[name=room]').value
    };

    if (payload.name === "") {
      SwalMixin.fire(
        "Uh oh...", "New Account needs a name", "error"
      );

      return;
    }

    FetchUtil.post(this.endpoint, payload, {
      successText: "User has been created."
    });
  }
}
