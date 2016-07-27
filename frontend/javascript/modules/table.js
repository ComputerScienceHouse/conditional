import $ from "jquery";
import dt from "datatables.net-bs";

export default class Table {
    constructor(table) {
        this.table = table;
        this.paginated = this.table.dataset.paginated;
        
        // Explicitly initialize DataTables
        dt(window, $);

        this.table = $(table).DataTable({
            "searching": false,
            "lengthChange": false,
            "info": false,
            "paging": this.paginated === 'false' ? false : true,
            "pagingType": "numbers"
        });

        this.table.order([1, "desc"]);
        this.render();
    }

    render() {
        this.table.draw();
    }
}
