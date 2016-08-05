import {Dropzone as dropzone} from "dropzone";
dropzone.autoDiscover = false;

export default class DropzoneUpload {
  constructor(element) {
    this.element = element;

    dropzone(this.element);
  }
}

dropzone.options.uploadUser = {
  acceptedFiles: ".csv"
};
