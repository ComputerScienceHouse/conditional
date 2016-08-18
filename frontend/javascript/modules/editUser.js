/* global fetch */
import "whatwg-fetch";
import FetchUtil from "../utils/fetchUtil";

export default class EditUser {
  constructor(link) {
    this.link = link;
    this.modal = document.querySelector('#' + this.link.dataset.modal);
    this.uid = this.link.dataset.uid;

    this.endpoints = {
      userDetails: '/manage/user/',
      alterHmAttendance: '/attendance/alter/hm/'
    };

    this.render();
  }

  render() {
    this.link.addEventListener("click", e => {
      e.preventDefault();

      fetch(this.endpoints.userDetails + this.uid)
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
    modal.setAttribute("id",
        this.modal.getAttribute("id") + "-" + this.uid);

    // Member Name
    modal.querySelector('#memberName').value = this.data.name;
    modal.querySelector('#memberName').disabled = true;

    // Room Number
    modal.querySelector('#room').value = this.data.room_number;
    if (this.data.room_number === "N/A") {
      modal.querySelector('#room').disabled = true;
      modal.querySelector('input[name=onfloor]').checked = false;
    } else {
      modal.querySelector('input[name=onfloor]').checked = true;
    }

    // Dues
    modal.querySelector('input[name=dues]').checked =
        this.data.active_member;

    // Housing Points
    modal.querySelector('#points').value = this.data.housing_points;

    // Missed House Meetings
    if (this.data.missed_hm.length > 0) {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('#noMissedHmAlert'));

      let missedHmTpl = modal.querySelector('#missedHmTpl');
      modal.querySelector(".modal-body").removeChild(missedHmTpl);

      this.data.missed_hm.forEach(hm => {
        let node = missedHmTpl.cloneNode(true);

        node.setAttribute("id", "missedHm-" + this.uid + "-" + hm.id);
        node.dataset.id = hm.id;

        node.querySelector(".hm-date").textContent = hm.date;

        if (hm.status === "Excused") {
          node.querySelector("input[name=hm-excused]").checked = true;
          node.querySelector("#reason").value = hm.excuse;
        }

        node.querySelector("input[name=hm-excused]").addEventListener(
            'click', e => e.target.classList.add('status-changed')
        );

        node.querySelector("#reason").addEventListener(
            'input', e => e.target.classList.add('excuse-changed')
        );

        node.querySelector("#markPresentBtn").addEventListener("click", e => {
          e.preventDefault();
          this._markMissedHmAsPresent(hm.id);
        });

        modal.querySelector(".modal-body").appendChild(node);
      });
    } else {
      modal.querySelector('.modal-body')
          .removeChild(modal.querySelector('#missedHmTpl'));
    }

    // Save button
    modal.querySelector('#editSaveBtn').addEventListener('click', e => {
      this._submitForm("#" + this.modal.getAttribute("id") + "-" + this.uid);
    });

    // Add to DOM and show, then remove on hide
    document.getElementsByTagName("body")[0].appendChild(modal);
    $("#" + this.modal.getAttribute("id") + "-" + this.uid)
        .on('hidden.bs.modal', e => {
          document.getElementsByTagName("body")[0].removeChild(e.target);
        })
        .modal('show');
  }

  _markMissedHmAsPresent(id) {
    FetchUtil.getWithWarning(
        this.endpoints.alterHmAttendance + this.uid + "/" + id, {
          warningText: "You will not be able to re-mark this user as absent " +
          "once they have been marked as present.",
          successText: "User has been marked as present."
        }, () => {
          $("#missedHm-" + this.uid + "-" + id).fadeOut();
        }
    );
  }

  _submitForm(modalSelector) {
    let modal = document.querySelector(modalSelector);
    console.log("Coming soon...");
    console.log(modal);
  }
}
