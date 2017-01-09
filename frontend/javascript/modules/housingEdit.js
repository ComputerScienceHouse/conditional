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
      alterRoom: '/housing/update/',
      memberDetails: '/member/'
    };

    this.render();
  }

  render() {
    this.link.addEventListener('click', e => {
      e.preventDefault();

      if (this.rmnumber !== "") { // eslint-disable-line no-negated-condition
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
        // Hide the modal.
        $(this.modal).modal('hide');

        // Update the DOM to reflect the new occupants.
        var occupantList = document.getElementById(room);
        if (occupantList) {
          // The room already exists in the list, update it.
          occupantList.innerHTML = '';
          payload.occupants.forEach(occupant => {
            fetch(this.endpoints.memberDetails + occupant, {
              method: 'GET',
              headers: {
                Accept: 'application/json'
              },
              credentials: 'same-origin'
            })
                .then(FetchUtil.checkStatus)
                .then(FetchUtil.parseJSON)
                .then(data => {
                  var newName = document.createElement("li");
                  newName.appendChild(document.createTextNode(data.name));
                  newName.setAttribute("class", "room-name");
                  occupantList.appendChild(newName);
                });
          });
        } else {
          // The room is new and needs to be created.
          var roomTable = document.getElementById("housing-table");
          var newRoom = document.createElement("tr");
          var newRoomNbrCol = document.createElement("td");
          var newRoomNbr = document.createElement("h3");
          newRoomNbr.appendChild(document.createTextNode(room));
          newRoomNbr.setAttribute("class", "room-number");
          newRoomNbrCol.appendChild(newRoomNbr);
          newRoomNbrCol.setAttribute("class", "new-table-col");
          newRoom.appendChild(newRoomNbrCol);
          // Add new occupants to room.
          var newOccupantCol = document.createElement("td");
          var newOccupantList = document.createElement("ul");
          newOccupantList.setAttribute("id", room);
          newOccupantList.setAttribute("class", "occupant-list");
          payload.occupants.forEach(occupant => {
            fetch(this.endpoints.memberDetails + occupant, {
              method: 'GET',
              headers: {
                Accept: 'application/json'
              },
              credentials: 'same-origin'
            })
                .then(FetchUtil.checkStatus)
                .then(FetchUtil.parseJSON)
                .then(data => {
                  var newName = document.createElement("li");
                  newName.appendChild(document.createTextNode(data.name));
                  newName.setAttribute("class", "room-name");
                  newOccupantList.appendChild(newName);
                });
          });
          newOccupantCol.appendChild(newOccupantList);
          newOccupantCol.setAttribute("class", "new-table-col");
          newRoom.appendChild(newOccupantCol);
          // Add edit button for new room.
          var newEditCol = document.createElement("td");
          var editBtn = document.getElementById("rm-edit-btn");
          var newEditBtn = editBtn.cloneNode(true);
          newEditBtn.setAttribute("data-rmnumber", room);
          new EditHousing(newEditBtn); // eslint-disable-no-new
          newEditCol.appendChild(newEditBtn);
          newEditCol.setAttribute("class", "new-table-col");
          newRoom.appendChild(newEditCol);
          roomTable.appendChild(newRoom);
        }
      });
    } else {
      throw new Exception(CmAttendanceException.SUBMIT_BEFORE_RENDER);
    }
  }
}
