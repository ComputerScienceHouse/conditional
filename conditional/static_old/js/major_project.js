$(document).ready(function () {

    projects = $("#projects").children()
    projects.each(function (project) {
        var project = projects[project];
        var id = project.attributes.project_id.value;

        $("#fail-" + id).click(function (e) {
            e.preventDefault();
            $.ajax({
                url: '/major_project/review',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                data: JSON.stringify({
                    "id": id,
                    "status": "Failed"
                }),
                error: function () {
                    alertify.error("Error reviewing major project.");
                },
                success: function (res) {
                    alertify.success("Major project reviewed successfully.");
                }
            });
        });
        $("#pass-" + id).click(function (e) {
            e.preventDefault();
            $.ajax({
                url: '/major_project/review',
                type: 'POST',
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                data: JSON.stringify({
                    "id": id,
                    "status": "Passed"
                }),
                error: function () {
                    alertify.error("Error reviewing major project.");
                },
                success: function (res) {
                    alertify.success("Major project reviewed successfully.");
                }
            });
        });
    });
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
