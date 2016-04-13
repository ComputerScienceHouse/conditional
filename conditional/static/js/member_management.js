$(document).ready(function () {
    // Initialize date picker
    // Disable submit on enter

    $("#submit-settings").click(function (e) {
        var housing_form = $("input:radio[name=housing_form]:checked").val();
        var intro_form = $("input:radio[name=intro_form]:checked").val();
        var site_locked = $("input:radio[name=site_lockdown]:checked").val();

        $.ajax({
            url: '/manage/settings',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'housing': housing_form,
                'intro': intro_form,
                'lockdown': site_locked
            }),
            error: function () {
                alertify.error("Error changing site settings.");
            },
            success: function () {
                alertify.success("Site settings changed successfully.");
            }
        });

    });
});
