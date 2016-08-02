/* global $ */
import "datatables.net-bs";

export default class Table {
    constructor(table) {
        this.table = table;

        // Set options based on data attributes
        this.paginated = this.table.dataset.paginated === 'false' ? false : true;
        this.sortColumn = !isNaN(this.table.dataset.sortColumn) ? this.table.dataset.sortColumn : 1;
        this.sortOrder = this.table.dataset.sortOrder === "asc" ? "asc" : "desc";
        this.lengthChangable = this.table.dataset.lengthChangable === 'true' ? true : false;

        // Just remove the search input from the DOM instead of disabling search all together
        this.domOptions = "l" + this.table.dataset.searchable === 'true' ? "t" : "" + "rtip";

        this.render();
    }

    render() {
        this.table = $(this.table).DataTable({
            "sDom": this.domOptions,
            "lengthChange": this.lengthChangable,
            "info": false,
            "paging": this.paginated,
            "pagingType": "numbers"
        })
            .order([this.sortColumn, this.sortOrder])
            .draw();
    }
}
