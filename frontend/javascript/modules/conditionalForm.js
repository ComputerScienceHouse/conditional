import FetchUtil from "../utils/fetchUtil";

export default class ConditionalForm {
  constructor(form) {
    this.form = form;
    this.endpoint = '/conditionals/create';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
            .addEventListener('click', e => this._submitForm(e));
  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      uid: this.form.querySelector('select[name=uid]').value,
      description: this.form.querySelector('input[name=description]').value,
      dueDate: this.form.querySelector('input[name=due_date]').value
    };

    FetchUtil.postWithWarning(this.endpoint, payload, {
      warningText: "Are you sure you want to create this conditional?",
      successText: "The conditional has been created."
    }, () => {
      $(this.form.closest('.modal')).modal('hide');
      location.reload();
    });
  }
}
