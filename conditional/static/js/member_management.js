$(document).ready(function () {
    // Initialize date picker
    // Disable submit on enter

    $("#financial-form").hide();
    $("#eval-form").hide();

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
    $.ajax({
        url: '/attendance/cm_members',
        type: 'GET',
        error: function (e) {
            console.error(e.responseText);
        },
        success: function (res) {
            $("#user").selectize({
                create: false,
                maxItems: 1,
                valueField: 'value',
                sortField: 'display',
                labelField: 'display',
                searchField: 'display',
                options: res.members,
                onItemAdd: function ( val, item) {
                    $.ajax({
                        url: '/manage/getuserinfo',
                        type: 'POST',
                        contentType: "application/json; charset=utf-8",
                        dataType: 'json',
                        data: JSON.stringify({
                            "uid": val
                        }),
                        success: function (res) {
                            // show form for eval/financial
                            $("#" + res.user + "-form").show();
                            console.log(res)
                            if(res.user == "financial") {
                                $('#dues_checkbox_financial').prop('checked', res.active_member);
                                $("#submit-financial").unbind('click');
                                $("#submit-financial").click(function (e) {
                                    e.preventDefault();
                                    $.ajax({
                                        url: '/manage/edituser',
                                        type: 'POST',
                                        contentType: "application/json; charset=utf-8",
                                        dataType: 'json',
                                        data: JSON.stringify({
                                            "uid": val,
                                            "active_member": $("#dues_checkbox_financial").is(':checked')
                                        }),
                                        success: function (res) {
                                            alertify.success("Site settings changed successfully.");
                                        }
                                    });
                                });
                            } else {
                                $('#dues_checkbox_eval').prop('checked', res.active_member);
                                $('#onfloor_checkbox_eval').prop('checked', res.onfloor_status);
                                $('#roomNum-eval').val(res.room_number);
                                $('#housePts-eval').val(res.housing_points);
                                $("#submit-eval").unbind('click');
                                $("#submit-eval").click(function (e) {
                                    e.preventDefault();
                                    $.ajax({
                                        url: '/manage/edituser',
                                        type: 'POST',
                                        contentType: "application/json; charset=utf-8",
                                        dataType: 'json',
                                        data: JSON.stringify({
                                            "uid": val,
                                            "active_member": $("#dues_checkbox_eval").is(':checked'),
                                            "onfloor_status": $("#onfloor_checkbox_eval").is(':checked'),
                                            "room_number": $("#roomNum-eval").val(),
                                            "housing_points": $("#housePts-eval").val()
                                        }),
                                        success: function (res) {
                                            alertify.success("Site settings changed successfully.");
                                        }
                                    });
                                });
                            }
                        }
                    });
                }
            });
        }
    });
});
