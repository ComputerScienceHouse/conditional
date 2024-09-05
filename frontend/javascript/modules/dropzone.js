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

Dropzone.options.projectFiles = {
    // autoQueue:false,
    url: "/major_project/upload",
    parallelUploads: 2,
    uploadMultiple: true,
    acceptedFiles: "audio/*,photo/*,video/*,.pdf,.doc,.docx"
}
console.load("loaded")