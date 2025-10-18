import Dropzone from "dropzone";
Dropzone.autoDiscover = false;

export default class DropzoneUpload {
  constructor(element) {
    this.element = element;
    this.render();
  }

  render() {
    const dz = new Dropzone(this.element); // eslint-disable-line new-cap
    dz.on("complete", () => window.location.reload());
  }
}

Dropzone.options.uploadUser = {
  acceptedFiles: ".csv"
};
