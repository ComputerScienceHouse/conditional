/* global fetch */
import 'whatwg-fetch';
import FetchUtil from '../utils/fetchUtil';
import MemberUtil from '../utils/memberUtil';
import MemberSelect from './memberSelect';

export default class EditMeeting {
  constructor(link) {
    this.link = link;
    this.modal = document.querySelector('#' + this.link.dataset.modal);
    this.type = this.modal.dataset.type;
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
    let modal = this.modal.cloneNode(true);
    modal.setAttribute('id',
        this.modal.getAttribute('id') + '-' + this.cid);

    // Submit button
    modal.querySelector('input[type="submit"]').addEventListener('click',
    e => {
      this._submitForm('#' + this.modal.getAttribute('id') + '-' + this.cid);
    });

    // Attendees
    const attendeesInput = modal.querySelector('input[name="attendees"]');
    let attendeesStr = "";
    this.data.attendees.forEach(attendee => {
      attendeesStr += attendee.value + ",";
    });
    attendeesInput.value = attendeesStr;

    // Initialize selector control
    attendeesInput.dataset.src = "cm_members";
    new MemberSelect(attendeesInput); // eslint-disable-line no-new

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName('body')[0].appendChild(modal);
    $('#' + this.modal.getAttribute('id') + '-' + this.cid)
        .on('hidden.bs.modal', e => {
          document.getElementsByTagName('body')[0].removeChild(e.target);
        })
        .modal('show');
  }

  _submitForm() {
    let modal = document.querySelector('#' + this.modal.getAttribute('id') +
        '-' + this.cid);

    modal.querySelectorAll('button').forEach(btn => {
      btn.disabled = true;
    });

    // Save details
    let payload = {};
    let membersSplit = MemberUtil.splitFreshmenUpperclassmen(
      this.fields.attendees.value.split(',')
    );
    payload.freshmen = membersSplit.freshmen;
    payload.members = membersSplit.upperclassmen;

    FetchUtil.post(this.endpoints.alterCmAttendance + this.cid, payload, {
      successText: 'Meeting attendance has been updated.'
    }, () => {
      $(modal).modal('hide');
    });
  }

}
