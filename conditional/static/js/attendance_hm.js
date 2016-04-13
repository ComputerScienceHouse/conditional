var DELIMITER = ",";

$(document).ready(function () {
    $.ajax({
        url: '/attendance/cm_members',
        type: 'GET',
        error: function (e) {
            console.error(e.responseText);
        },
        success: function (res) {
            $("#attendees").selectize({
                delimiter: DELIMITER,
                persist: false,
                valueField: 'value',
                labelField: 'display',
                searchField: 'display',
                selectOnTab: true,
                options: res.members
            });
        }
    });

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
