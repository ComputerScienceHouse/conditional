$(document).ready(function () {
    $.ajax({
        url: '/attendance/cm_members',
        type: 'GET',
        error: function (e) {
            console.error(e.responseText);
        },
        success: function (res) {
            $("#attendees").selectize({
                delimiter: ',',
                persist: false,
                valueField: 'value',
                labelField: 'display',
                searchField: 'display',
                selectOnTab: true,
                options: res.members
            });
        }
    });
});