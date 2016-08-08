$(document).ready(function () {
    // Initialize date picker
    // Disable submit on enter


    function addMissedHM(date, hm_id, attend_status) {
        console.log(date + " " + hm_id + " " + attend_status)
        $("#hm_template0").clone()
            .appendTo("#missed_hms")
            .attr("id", "hm-" + hm_id)
            .find('*')
            .each(function() {
                var id = this.id || "";
                // Get the non-number part of the divid
                var match = id.match(/^(.+?)(\d+)$/i) || [];
                if (match.length == 3) {
                    this.id = match[1] + (hm_id);
                }
            });
        $('#excused-' + hm_id).prop('checked', attend_status == "Excused");
        $("#hm-" + hm_id).show()
        $("#date-" + hm_id).html(date)
    }

    $("#financial-form").hide();
    $("#fid-form").hide();
    $("#eval-form").hide();
    $("#hm_template0").hide();
    $("#submit-eval").hide();

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

    $("input:checkbox[name=housing_form_checkbox]").change(function () {
        $.ajax({
            url: '/manage/settings',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'housing': this.checked
            }),
            error: function () {
                alertify.error("Error changing site settings.");
            },
            success: function () {
                alertify.success("Site settings changed successfully.");
            }
        });
    });

    $("input:checkbox[name=intro_form_checkbox]").change(function () {
        $.ajax({
            url: '/manage/settings',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'intro': this.checked
            }),
            error: function () {
                alertify.error("Error changing site settings.");
            },
            success: function () {
                alertify.success("Site settings changed successfully.");
            }
        });
    });

    $("input:checkbox[name=site_lockdown_checkbox]").change(function () {
        $.ajax({
            url: '/manage/settings',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'site_lockdown': this.checked
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
                            $("#financial-form").hide();
                            $("#fid-form").hide();
                            $("#eval-form").hide();
                            $("#hm_template0").hide();
                            $("#submit-eval").hide();
                            $("#missed_hms").empty()
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
                                            $("#financial-form").hide();
                                            alertify.success("Site settings changed successfully.");
                                        }
                                    });
                                });
                            } else if (res.user == "fid") {
                                $("#submit-fid").unbind('click');
                                $("#submit-fid").click(function (e) {
                                    e.preventDefault();
                                    $.ajax({
                                        url: '/manage/upgrade_user',
                                        type: 'POST',
                                        contentType: "application/json; charset=utf-8",
                                        dataType: 'json',
                                        data: JSON.stringify({
                                            "fid": val,
                                            "uid": $("#uid-fid").val(),
                                            "sigsMissed": $("#sigsMissed-fid").val()
                                        }),
                                        success: function (res) {
                                            $("#fid-form").hide();
                                            alertify.success("Upgraded User!");
                                            window.reload();
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
                                            $("#eval-form").hide();
                                            alertify.success("Site settings changed successfully.");
                                        }
                                    });
                                });
                                $("#submit-eval").show()
                                $("#missed_hms").empty()
                                for (var i = 0; i < res.missed_hm.length; i++) {
                                    hm = res.missed_hm[i]
                                    addMissedHM(hm.date, hm.id, hm.status);
                                    // Show comment box when add comment is clicked
                                    $('.comment-trigger').click(function () {
                                        $(this).hide();
                                        $(this).siblings(".comment-field").show();
                                    });

                                }
                            }
                        }
                    });
                }
            });
        }
    });
});
