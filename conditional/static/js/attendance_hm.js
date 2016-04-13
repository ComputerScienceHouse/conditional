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
    $('.attendance-Attended').click(function () {
        $(this).addClass('btn-success').siblings().removeClass('btn-danger').removeClass('btn-info');
    });

    $('.attendance-Absent').click(function () {
        $(this).addClass('btn-danger').siblings().removeClass('btn-success').removeClass('btn-info');
    });

    $('.attendance-Excused').click(function () {
        $(this).addClass('btn-info').siblings().removeClass('btn-success').removeClass('btn-danger');
    });

    // Show comment box when add comment is clicked
    $('.comment-trigger').click(function () {
        $(this).hide();
        $(this).siblings(".comment-field").show();
    });

    $("#submit").click(function (e) {
        e.preventDefault();

        rows = $("#attendees").children()

        var freshmen = [];
        var upperclassmen = [];

        rows.each(function (row) {
            row = rows[row];
            member = row.attributes.member.value;
            status = $("input:radio[name=attendance-" + member + "]:checked").val()
            excuse = $("#comment-" + member).val()

            if (!isNaN(member)) {
                freshmen.push({
                    'id': member,
                    'excuse': excuse,
                    'status': status
                })
            } else {
                upperclassmen.push({
                    'uid': member,
                    'excuse': excuse,
                    'status': status
                })
            }
        });

        $.ajax({
            url: '/attendance/submit/hm',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                "freshmen": freshmen,
                "members": upperclassmen,
                "timestamp": $("#date").val()
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
