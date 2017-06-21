/* global $ */
import _ from "lodash";
import "datatables.net-bs";

export default class Table {
  constructor(table) {
    this.table = table;

    // Set options based on data attributes
    this.sortColumn = (_.isNil(this.table.dataset.sortColumn) ||
                        _.isNaN(this.table.dataset.sortColumn)) ?
                        1 : this.table.dataset.sortColumn;
    this.sortOrder = this.table.dataset.sortOrder === "asc" ? "asc" : "desc";

    this.options = {
      lengthChange: this.table.dataset.lengthChangable === 'true',
      info: false,
      paging: !(this.table.dataset.paginated === 'false'),
      pagingType: "numbers",
      order: [],
      pageLength: this.table.dataset.pageLength || 10
    };

    // Just remove the search input from the DOM instead of disabling it
    if (this.table.dataset.searchable !== 'true') {
      this.options.dom = "lrtip";
    }

    this.render();
  }

  render() {
    this.table = $(this.table).DataTable(this.options) // eslint-disable-line new-cap
      .order([this.sortColumn, this.sortOrder])
      .draw();
  }
}
