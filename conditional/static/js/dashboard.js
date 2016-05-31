$(function () {
    var table = $("table.paginated").DataTable({
        "searching": false,
        "lengthChange": false,
        "info": false,
        "pagingType": "numbers"
    });

    table.order([1, "asc"])
    table.draw()
});
