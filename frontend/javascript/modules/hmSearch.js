/* global $ */
import Exception from "../exceptions/exception";
import HmSearchException from "../exceptions/hmSearchException";

export default class HouseMeetingSearch {
  constructor(input) {
    this.input = input;
    this.target = document.querySelector(this.input.dataset.target);

    if (this.target === null) {
      throw new Exception(HmSearchException.TARGET_REQUIRED);
    }

    if (this.target.tagName !== "TABLE") {
      throw new Exception(HmSearchException.NOT_A_TABLE);
    }

    // Is the target already a DataTable?
    if ($.fn.dataTable && $.fn.dataTable.isDataTable(this.target)) {
      // Yes, render
      this.render();
    } else {
      // No, wait until it initializes before rendering
      // Must use jQuery to listen to events fired by DataTables
      $(this.target).on("init.dt", () => this.render());
    }
  }

  render() {
    // Remove the event listner so this module doesn't try to render again
    $(this.target).off("init.dt");

    // Add custom filtering function
    $.fn.dataTable.ext.search.push(HouseMeetingSearch._alreadySelectedFilter);

    // Retrieve the target's DataTable API object
    this.api = $(this.target).DataTable({ // eslint-disable-line new-cap
      retrieve: true
    });

    // Bind to the input
    this.input.addEventListener("keydown", event => this._handleKey(event));
  }

  _handleKey(event) {
    // Did the user press enter?
    let keyCode = event.keyCode || event.which;
    if (keyCode === 13) {
      // Yes, prevent form submission
      event.preventDefault();

      this._handleKeyAction();

      // Reset the table
      this.api.search('').draw();

      // Clear and refocus input
      this.input.value = "";
      this.input.focus();
    } else {
      // No, search and redraw the table
      this.api.search(this.input.value).draw();
    }
  }

  _handleKeyAction() {
    // Check the first visible table row's checkbox
    this.api.table().body().firstElementChild
      .querySelector("input[type=checkbox]").checked = true;
  }

  /*
   * Custom filtering function that will remove rows that are already selected
   */
  static _alreadySelectedFilter(settings, data, dataIndex) {
    // Only apply the filter if we're currently searching
    if (typeof settings.oPreviousSearch.sSearch !== "undefined" &&
        settings.oPreviousSearch.sSearch !== "") {
      return !settings.aoData[dataIndex].anCells[1]
        .querySelector("input[type=checkbox]").checked;
    }

    return true;
  }
}
