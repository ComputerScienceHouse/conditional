export default class EvalToggle {
  constructor(toggle) {
    this.toggle = toggle;

    this.render();
  }

  render() {
    this.toggle.addEventListener('click', () => {
      this._toggleTable();
    });
  }

  _toggleTable() {
    if (this.toggle.checked) {
      $("#eval-blocks").hide();
      $("#eval-table").show();
    } else {
      $("#eval-table").hide();
      $("#eval-blocks").show();
    }
  }
}
