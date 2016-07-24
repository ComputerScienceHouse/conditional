import $ from "jquery";
import dt from "datatables.net-bs";

export default class Table {
    constructor(table) {
        dt(window, $);

        this.table = $(table).DataTable({
            "searching": false,
            "lengthChange": false,
            "info": false,
            "pagingType": "numbers"
        });

        this.table.order([1, "desc"]);
        this.render();
    }

    render() {
        this.table.draw();
    }
}
