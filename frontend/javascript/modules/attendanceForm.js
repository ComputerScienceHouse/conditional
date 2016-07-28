/* global fetch */
import "whatwg-fetch";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";
import MemberUtil from "../utils/memberUtil";
import sweetAlert from "../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js";

export default class AttendanceForm {
    constructor(form) {
        this.form = form;
        
        this.fields = {
            "timestamp": this.form.elements["date"],
            "attendees": this.form.elements["attendees"]
        };
        
        this.endpoint = '';
        
        if (this.form.dataset.type === "committee") {
            this.endpoint = '/attendance/submit/cm';
            this.fields["committee"] = this.form.elements["committee"];
        } else if (this.form.dataset.type === "seminar") {
            this.endpoint = '/attendance/submit/ts';
            this.fields["name"] = this.form.elements["name"];
        }

        this.render();
    }

    render() {
        // Prevent the form from submitting if the user hits the enter key
        ['keyup', 'keypress'].forEach((keyevent) => this.form.addEventListener(keyevent, (event) => {
            var keyCode = event.keyCode || event.which;
            if (keyCode === 13) {
                event.preventDefault();
                return false;
            }
        }, true));

        // Form submit handler
        this.form.querySelectorAll("input[type=submit]").forEach((submitBtn) => {
            submitBtn.addEventListener("click", (e) => {
                e.preventDefault();
                let payload = {};

                Object.keys(this.fields).forEach((field) => {
                    if (field == "attendees") {
                        let membersSplit = MemberUtil.splitFreshmenUpperclassmen(this.fields[field].value.split(','));
                        payload["freshmen"] = membersSplit.freshmen;
                        payload["members"] = membersSplit.upperclassmen;
                    } else {
                        payload[field] = this.fields[field].value;
                    }
                });
                
                sweetAlert({
                    title: "Are you sure?",
                    text: "You will not be able to edit this event once attendance has been recorded.",
                    type: "warning",
                    showCancelButton: true,
                    closeOnConfirm: false,
                    showLoaderOnConfirm: true
                }, () => {
                    fetch(this.endpoint, {
                        method: 'POST',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    })
                        .then(FetchUtil.checkResponse)
                        .then(FetchUtil.parseJSON)
                        .then((response) => {
                            if(response.hasOwnProperty('success') && response.success === true) {
                                sweetAlert({
                                    title: "Success!",
                                    text: "Attendance has been submitted.",
                                    type: "success",
                                    confirmButtonText: "OK",
                                }, () => {
                                    window.location.reload();
                                });
                            } else {
                                sweetAlert("Uh oh...", "We're having trouble submitting attendance right now, please try again later.", "error");
                                throw new Exception(FetchException.REQUEST_FAILED, response);
                            }
                        })
                        .catch((error) => {
                            sweetAlert("Uh oh...", "We're having trouble submitting attendance right now, please try again later.", "error");
                            throw new Exception(FetchException.REQUEST_FAILED, error);
                        });
                });

                return false;
            });
        });
    }
}