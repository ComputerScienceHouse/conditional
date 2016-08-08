import Dropzone from "dropzone";
Dropzone.autoDiscover = false;

export default class DropzoneUpload {
  constructor(element) {
    this.element = element;

    new Dropzone(this.element); // eslint-disable-line new-cap,no-new
  }
}

Dropzone.options.uploadUser = {
  acceptedFiles: ".csv"
};
