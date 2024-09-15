import FetchUtil from "../utils/fetchUtil";

export default class MajorProjectForm {

  tags_written = false;

  constructor(form) {
    this.form = form;
    this.endpoint = '/major_project/submit';
    this.render();
  }

  render() {
    this.form.querySelector('input[type=submit]')
      .addEventListener('click', e => this._submitForm(e));
    this.form.querySelector('input[id=skill-input]')
        .addEventListener('focusout')
  }

  onWriteSkill(e) {
    let input = document.getElementById("skill-input")
    if (!this.tags_written) {
      this.tags_written = true
      document.getElementsByClassName("placeholder").item(0).remove()
    }
        let txt = input.value.replace(/[^a-zA-Z0-9\+\-\.\#]/g, ''); // allowed characters list
    if (txt) input.before('<span class="skill-tag">' + txt + '</span>');
    input.value = "";
    input.focus();

  }

  _submitForm(e) {
    e.preventDefault();

    let payload = {
      projectName: this.form.querySelector('input[name=name]').value,
      projectTldr: this.form.querySelector('input[name=tldr]').value,
      projectTimeSpent: this.form.querySelector('textarea[name=time-commitment]').value,
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
