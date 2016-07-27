import Dropzone from "dropzone";
Dropzone.autoDiscover = false;

export default class DropzoneUpload {
    constructor (element) {
        this.element = element;
        
        const dz = new Dropzone(this.element);
    }
}

Dropzone.options.uploadUser = {
    acceptedFiles: ".csv"
}