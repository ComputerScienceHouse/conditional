var DELIMITER = ",";

$(document).ready(function () {
    // Initialize date picker
    $('#date').bootstrapMaterialDatePicker({weekStart: 0, time: false});

    // Disable submit on enter
    $('#hmAttendanceForm').on('keyup keypress', function (e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13) {
            e.preventDefault();
            return false;
        }
    });

    // Update attendance picker colors when changed
    $('.attendance-present').click(function () {
        $(this).addClass('btn-success').siblings().removeClass('btn-danger').removeClass('btn-info');
    });

    $('.attendance-absent').click(function () {
        $(this).addClass('btn-danger').siblings().removeClass('btn-success').removeClass('btn-info');
    });

    $('.attendance-excused').click(function () {
        $(this).addClass('btn-info').siblings().removeClass('btn-success').removeClass('btn-danger');
    });

    // Show comment box when add comment is clicked
    $('.comment-trigger').click(function() {
        $(this).hide();
        $(this).siblings(".comment-field").show();
    });

    $("#submit").click(function (e) {
        e.preventDefault();

        var attendees = $("#attendees").val().split(DELIMITER);
        var freshmen = [];
        var upperclassmen = [];
        $.each(attendees, function (memberId) {
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
