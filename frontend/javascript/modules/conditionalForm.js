import FetchUtil from "../utils/fetchUtil";
import reveal from 'reveal.js';

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
    let uid = this.form.uid.value;
    let evaluation = null;
    if (location.pathname.split('/')[1] === "slideshow") {
      evaluation = location.pathname.split('/')[2];
    }
    let payload = {
      uid: uid,
      description: this.form.querySelector('input[name=description]').value,
      dueDate: this.form.querySelector('input[name=due_date]').value,
      evaluation: evaluation
    };
    FetchUtil.postWithWarning(this.endpoint, payload, {
      warningText: "Are you sure you want to create this conditional?",
      successText: "The conditional has been created."
    }, () => {
      $(this.form.closest('.modal')).modal('hide');
      if (location.pathname.split('/')[1] === "slideshow") {
        $('#createConditional').on('hidden.bs.modal', function() {
          var condBtn = $('div[data-uid="' + uid + '"] button')
          .first();
          $(condBtn).text("Conditionaled").off("click").addClass("disabled");
          $(condBtn).next().hide();
        });
        reveal.right();
      } else {
        location.reload();
      }
    });
  }
}
