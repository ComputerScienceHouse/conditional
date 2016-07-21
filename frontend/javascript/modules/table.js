import dt from "datatables.net-bs";

export default class Table {
    constructor(table) {
        dt(window, jQuery);

        this.table = jQuery(table).DataTable({
            "searching": false,
            "lengthChange": false,
            "info": false,
            "pagingType": "numbers"
        });

        this.table.order([1, "asc"]);
        this.render();
    }

    render() {
        this.table.draw();
    }
}