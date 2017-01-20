/* global fetch */
import 'whatwg-fetch';
import Exception from '../exceptions/exception';
import FetchException from '../exceptions/fetchException';
import FetchUtil from '../utils/fetchUtil';
import sweetAlert from '../../../node_modules/bootstrap-sweetalert/dev/sweetalert.es6.js'; // eslint-disable-line max-len

export default class HousingQueue {
  constructor(queuePanel) {
    this.queuePanel = queuePanel;
    this.queueTable = this.queuePanel.querySelector('table');
    this.endpoint = '/housing/in_queue';
    this.filteredState = false;

    // Is the housing queue already a DataTable?
    if ($.fn.dataTable && $.fn.dataTable.isDataTable(this.queueTable)) {
      // Yes, render
      this.render();
    } else {
      // No, wait until it initializes before rendering
      // Must use jQuery to listen to events fired by DataTables
      $(this.queueTable).on('init.dt', () => this.render());
    }
  }

  render() {
    // Remove the event listner so this module doesn't try to render again
    $(this.queueTable).off('init.dt');

    // Retrieve the queue table's DataTables API object
    this.queueTableApi = $(this.queueTable).DataTable({ // eslint-disable-line new-cap
      retrieve: true
    });

    // Add custom filtering function
    $.fn.dataTable.ext.afnFiltering.push(HousingQueue._inQueueFilter);

    this.bindFilterButton();
    this.bindCheckboxes();
  }

  bindFilterButton() {
    const filterButton = this.queuePanel.querySelector('#queueFilterToggle');
    filterButton.addEventListener('click', () => {
      if (this.queueTable.dataset.show === 'all') {
        filterButton.innerHTML =
            filterButton.innerHTML.replace('Show Current Queue', 'Show All');
        this.queueTable.dataset.show = 'current';
      } else {
        filterButton.innerHTML =
            filterButton.innerHTML.replace('Show All', 'Show Current Queue');
        this.queueTable.dataset.show = 'all';
      }

      this.queueTableApi.draw();
    });
  }

  bindCheckboxes() {
    this.queuePanel.querySelectorAll('.col-in-queue > input[type="checkbox"]')
        .forEach(toggle => {
          toggle.addEventListener('click', () => {
            const row = toggle.parentNode.parentNode;
            this.updateInQueue(toggle.dataset.uid, toggle.checked, row);
          });
        });
  }

  updateInQueue(uid, inQueue, row) {
    let payload = {
      uid: uid,
      inQueue: inQueue
    };

    fetch(this.endpoint, {
      method: 'PUT',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    })
      .then(FetchUtil.checkStatus)
      .then(FetchUtil.parseJSON)
      .then(response => {
        if (response.hasOwnProperty('success') &&
          response.success === true) {
          if (inQueue) {
            row.classList.remove('disabled');
          } else {
            row.classList.add('disabled');
          }
        } else {
          sweetAlert('Uh oh...', 'We\'re having trouble updating ' +
            'the queue right now. Please try again later.', 'error');
          throw new Exception(FetchException.REQUEST_FAILED, response);
        }
      })
      .catch(error => {
        sweetAlert('Uh oh...', 'We\'re having trouble updating ' +
          'the queue right now. Please try again later.', 'error');
        throw new Exception(FetchException.REQUEST_FAILED, error);
      });
  }

  /*
   * Custom filtering function that will remove rows that are not in the housing queue (unselected)
   */
  static _inQueueFilter(settings, data, dataIndex) {
    // Check to see if we should apply the filter
    if (settings.nTable.dataset.show === 'current') {
      return settings.aoData[dataIndex].anCells[2]
            .querySelector('input[type=checkbox]').checked;
    }

    return true;
  }
}
