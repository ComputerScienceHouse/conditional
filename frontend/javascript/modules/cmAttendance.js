/* global fetch */
import 'whatwg-fetch';
import Exception from "../exceptions/exception";
import CmAttendanceException from "../exceptions/cmAttendanceException";
import FetchUtil from "../utils/fetchUtil";
import MemberUtil from "../utils/memberUtil";
import MemberSelect from "./memberSelect";

export default class EditMeeting {
  constructor(link) {
    this.link = link;
    this.modal = null;
    this.modalTpl = document.querySelector('#' + this.link.dataset.modal);
    this.type = this.modalTpl.dataset.type;
    this.cid = this.link.dataset.cid;

    this.endpoints = {
      meetingDetails: '/attendance/cm/',
      alterCmAttendance: '/attendance/alter/cm/'
    };

    this.render();
  }

  render() {
    this.link.addEventListener('click', e => {
      e.preventDefault();

      fetch(this.endpoints.meetingDetails + this.cid, {
        method: 'GET',
        headers: {
          Accept: 'application/json'
        },
        credentials: 'same-origin'
      })
          .then(FetchUtil.checkStatus)
          .then(FetchUtil.parseJSON)
          .then(data => {
            this.data = data;
            this._renderModal();
          });
    });
  }

  _renderModal() {
    // Clone template modal
    this.modal = this.modalTpl.cloneNode(true);
    this.modal.setAttribute('id',
        this.modal.getAttribute('id') + '-' + this.cid);

    // Submit button
    this.modal.querySelector('input[type="submit"]').addEventListener('click',
      e => {
        e.preventDefault();
        this._submitForm();
      });

    // Delete Button
    this.modal.querySelector('button.delete-btn').addEventListener('click', e =>
      this._deleteMeeting()
    );

    // Attendees
    const attendeesInput = this.modal.querySelector('input[name="attendees"]');
    let attendeesStr = "";
    this.data.attendees.forEach(attendee => {
      attendeesStr += attendee.value + ",";
    });
    attendeesInput.value = attendeesStr;

    // Initialize selector control
    attendeesInput.dataset.src = "cm_members";
    new MemberSelect(attendeesInput); // eslint-disable-line no-new

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName('body')[0].appendChild(this.modal);
    $(this.modal)
        .on('hidden.bs.modal', e => {
          document.getElementsByTagName('body')[0].removeChild(e.target);
        })
        .modal('show');
  }

  _submitForm() {
    if (this.modal) {
      this.modal.querySelectorAll('button').forEach(btn => {
        btn.disabled = true;
      });

      // Save details
      let payload = {};
      let membersSplit = MemberUtil.splitFreshmenUpperclassmen(
        this.modal.querySelector('input[name="attendees"]').value.split(',')
      );
      payload.freshmen = membersSplit.freshmen;
      payload.members = membersSplit.upperclassmen;

      FetchUtil.post(this.endpoints.alterCmAttendance + this.cid, payload, {
        successText: 'Meeting attendance has been updated.'
      }, () => {
        $(this.modal).modal('hide');
        window.location.reload();
      });
    } else {
      throw new Exception(CmAttendanceException.SUBMIT_BEFORE_RENDER);
    }
  }

  _deleteMeeting() {
    if (this.modal) {
      this.modal.querySelectorAll('button').forEach(btn => {
        btn.disabled = true;
      });

      // Delete details
      FetchUtil.fetchWithWarning(this.endpoints.meetingDetails + this.cid, {
        method: 'DELETE',
        warningText: "This meeting will be permanently deleted.",
        successText: "Meeting has been deleted."
      }, () => {
        $(this.modal).modal('hide');
        window.location.reload();
      });
    } else {
      throw new Exception(CmAttendanceException.SUBMIT_BEFORE_RENDER);
    }
  }

}
