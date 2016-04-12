$(document).ready(function () {
    $("#submit").click(function (e) {
        e.preventDefault();

        $.ajax({
            url: '/intro_evals/submit',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                "social_events": $("#social_events").val(),
                "comments": $("#comments").val(),
            }),
            error: function () {
                alertify.error("Error submitting intro evaluation.");
            },
            success: function (res) {
                alertify.success("Intro evaluation submitted successfully.");
            }
        });

    });
});
