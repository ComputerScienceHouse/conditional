$(document).ready(function () {
    $("#submit").click(function (e) {
        e.preventDefault();

        $.ajax({
            url: '/housing_evals/submit',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                "social_attended": $("#social_attended").val(),
                "social_hosted": $("#social_hosted").val(),
                "seminars_attended": $("#seminars_attended").val(),
                "seminars_hosted": $("#seminars_hosted").val(),
                "projects": $("#projects").val(),
                "comments": $("#comments").val(),
            }),
            error: function () {
                alertify.error("Error submitting housing evaluation.");
            },
            success: function (res) {
                alertify.success("Housing evaluation submitted successfully.");
            }
        });

    });
});
