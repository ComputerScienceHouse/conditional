import FetchUtil from '../utils/fetchUtil';

export default class NewYear {
  constructor(link) {
    this.link = link;
    this.step = this.link.dataset.step;

    this.endpoints = {
      housing: '/housing',
      active: '/manage/active'
    };

    this.render();
  }
  render() {
    this.link.addEventListener('click', e => {
      e.preventDefault();

      if (this.step === "welcome") {
        $('#new-welcome').fadeOut(function() {
          $("#new-clear").fadeIn();
        });
      } else if (this.step === "clear") {
        FetchUtil.fetchWithWarning(this.endpoints.active, {
          method: 'DELETE',
          warningText: "This will clear active members and room assignments!",
          successText: "Data successfully cleared."}, () => {
            fetch(this.endpoints.housing, {
              method: 'DELETE'
            })
            .then($('#new-clear').fadeOut(function() {
              $("#new-housing").fadeIn();
            })
            );
          });
      }
    });
  }
}
