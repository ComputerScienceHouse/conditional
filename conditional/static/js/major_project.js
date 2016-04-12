$(document).ready(function () {
    $("#submit").click(function (e) {
        e.preventDefault();

        $.ajax({
            url: '/major_project/submit',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                "project_name": $("#name").val(),
                "project_description": $("#description").val(),
            }),
            error: function () {
                alertify.error("Error submitting major project.");
            },
            success: function (res) {
                alertify.success("Major project submitted successfully.");
            }
        });

    });
});
