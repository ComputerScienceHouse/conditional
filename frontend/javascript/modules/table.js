/* global $ */
import "datatables.net-bs";

export default class Table {
  constructor(table) {
    this.table = table;

    // Set options based on data attributes
    this.paginated = !this.table.dataset.paginated === 'false';
    this.sortColumn = isNaN(this.table.dataset.sortColumn) ?
                        1 : this.table.dataset.sortColumn;
    this.sortOrder = this.table.dataset.sortOrder === "asc" ? "asc" : "desc";
    this.lengthChangable = this.table.dataset.lengthChangable === 'true';

    // Just remove the search input from the DOM instead of disabling it
    if (this.table.dataset.searchable !== 'true') {
      this.domOptions = "lrtip";
    }

    this.render();
  }

  render() {
    this.table = $(this.table).DataTable({ // eslint-disable-line new-cap
      sDom: this.domOptions,
      lengthChange: this.lengthChangable,
      info: false,
      paging: this.paginated,
      pagingType: "numbers"
    })
      .order([this.sortColumn, this.sortOrder])
      .draw();
  }
}
