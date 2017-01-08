/* global fetch */
import 'whatwg-fetch';
import Exception from "../exceptions/exception";
import CmAttendanceException from "../exceptions/cmAttendanceException";
import FetchUtil from "../utils/fetchUtil";
import MemberSelect from "./memberSelect";

export default class EditHousing {
  constructor(link) {
    this.link = link;
    this.modal = null;
    this.modalTpl = document.querySelector('#' + this.link.dataset.modal);
    this.type = this.modalTpl.dataset.type;
    this.rmnumber = this.link.dataset.rmnumber;

    this.endpoints = {
      roomDetails: '/housing/room/',
      alterRoom: '/housing/update/'
    };

    this.render();
  }

  render() {
    this.link.addEventListener('click', e => {
      e.preventDefault();

      if (this.rmnumber !== "") {
        fetch(this.endpoints.roomDetails + this.rmnumber, {
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
      } else {
        this.data = {};
        this.data.occupants = [];
        this._renderModal();
      }
    });
  }

  _renderModal() {
    // Clone template modal
    this.modal = this.modalTpl.cloneNode(true);
    this.modal.setAttribute('id',
        this.modal.getAttribute('id') + '-' + this.rmnumber);

    // Submit button
    this.modal.querySelector('input[type="submit"]').addEventListener('click',
      e => {
        e.preventDefault();
        this._submitForm();
      });

    // Room Number
    const roomInput = this.modal.querySelector('input[name="rmnumber"]');
    roomInput.value = this.rmnumber;

    // Occupants
    const occupantsInput = this.modal.querySelector('input[name="occupants"]');
    let occupantsStr = "";
    this.data.occupants.forEach(occupant => {
      occupantsStr += occupant + ",";
    });
    occupantsInput.value = occupantsStr;

    // Initialize selector control
    occupantsInput.dataset.src = "cm_members";
    new MemberSelect(occupantsInput); // eslint-disable-line no-new

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
      payload.occupants = this.modal.querySelector('input[name="occupants"]').value.split(','); // eslint-disable-line max-len
      let room = this.modal.querySelector('input[name="rmnumber"]').value;

      FetchUtil.post(this.endpoints.alterRoom + room, payload, {
        successText: 'Occupants have been updated.'
      }, () => {
        $(this.modal).modal('hide');
        window.location.reload();
      });
    } else {
      throw new Exception(CmAttendanceException.SUBMIT_BEFORE_RENDER);
    }
  }
}
