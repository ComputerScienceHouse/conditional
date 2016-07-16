$(document).ready(function () {

    conditionals = $("#conditionals").children()

    var skipHeader = true;
    conditionals.each(function (conditional) {

        if (skipHeader) {
            skipHeader = false;
            // continue
            return true;
        }
        var conditional = conditionals[conditional];
        var id = conditional.attributes.conditional_id.value;

        $("#fail-" + id).click(function (e) {
            e.preventDefault();
            $.ajax({
                url: '/conditionals/review',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                data: JSON.stringify({
                    "id": id,
                    "status": "Failed"
                }),
                error: function () {
                    alertify.error("Error reviewing conditional.");
                },
                success: function (res) {
                    alertify.success("Conditional reviewed successfully.");
                }
            });
        });
        $("#pass-" + id).click(function (e) {
            e.preventDefault();
            $.ajax({
                url: '/conditionals/review',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                data: JSON.stringify({
                    "id": id,
                    "status": "Passed"
                }),
                error: function () {
                    alertify.error("Error reviewing conditional.");
                },
                success: function (res) {
                    alertify.success("Conditional reviewed successfully.");
                }
            });
        });
    });
});
