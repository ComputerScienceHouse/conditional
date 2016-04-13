var DELIMITER = ",";

$(document).ready(function () {
    $('#hm_date').bootstrapMaterialDatePicker({ weekStart : 0, time: false });

    $("#submit").click(function (e) {
        e.preventDefault();

        var attendees = $("#attendees").val().split(DELIMITER);
        var freshmen = [];
        var upperclassmen = [];
        $.each(attendees, function(memberId) {
            memberId = attendees[memberId];
            if (!isNaN(memberId)) {
                // Numeric UID, freshman account
                freshmen.push(memberId);
            } else {
                // Upperclassman
                upperclassmen.push(memberId);
            }
        });

        $.ajax({
            url: '/attendance/submit/cm',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                "committee": $("#position").val(),
                "freshmen": freshmen,
                "members": upperclassmen
            }),
            error: function () {
                alertify.error("Error submitting attendance.");
            },
            success: function (res) {
                alertify.success("Attendance submitted successfully.");
            }
        });

    });
});
