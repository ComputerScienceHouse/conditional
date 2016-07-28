import $ from "jquery";
import dt from "datatables.net-bs";

export default class Table {
    constructor(table) {
        this.table = table;
        this.paginated = this.table.dataset.paginated;
        this.searchable = this.table.dataset.searchable;
        this.sortColumn = !isNaN(this.table.dataset.sortColumn) ? this.table.dataset.sortColumn : 1;
        this.sortOrder = this.table.dataset.sortOrder === "asc" ? "asc" : "desc";
        this.lengthChangable = this.table.dataset.lengthChangable;
        
        // Explicitly initialize DataTables
        dt(window, $);

        this.table = $(table).DataTable({
            "searching": this.searchable === 'true' ? true : false,
            "lengthChange": this.lengthChangable === 'true' ? true : false,
            "info": false,
            "paging": this.paginated === 'false' ? false : true,
            "pagingType": "numbers"
        });

        this.table.order([this.sortColumn, this.sortOrder]);
        this.render();
    }

    render() {
        this.table.draw();
    }
}
