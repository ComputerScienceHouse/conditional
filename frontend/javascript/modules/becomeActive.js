import FetchUtil from "../utils/fetchUtil";

export default class becomeActive {
  constructor(link) {
    this.link = link;
    this.endpoint = '/manage/make_user_active';
    this.render();
  }

  render() {
    this.link.addEventListener('click', e => this._delete(e));
  }

  _delete(e) {
    e.preventDefault();

    FetchUtil.postWithWarning(this.endpoint, {}, {
      warningText: "Becoming an active member means that you will be charged" +
                    " dues, which are $80 per semester.",
      successText: "You are now an active member."
    }, () => {
      document.getElementById('becomeActive').remove();
    });
  }
}

