import FetchUtil from "../utils/fetchUtil";

export default class coopDelete {
  constructor(link) {
    this.link = link;
    this.uid = this.link.dataset.uid;
    this.endpoint = '/co_op/' + this.uid;
    this.render();
  }

  render() {
    this.link.addEventListener('click', e => this._delete(e));
  }

  _delete(e) {
    e.preventDefault();

    FetchUtil.fetchWithWarning(this.endpoint, {
      method: 'DELETE',
      warningText: "This co-op entry will be deleted and the user will no" +
      " longer be excluded from attendance and vote counts.",
      successText: "Co-op has been deleted."
    }, () => {
      document.getElementById('coop-' + this.uid).remove();
    });
  }
}
