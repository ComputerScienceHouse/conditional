(function() {
    // Angular app
    var app = angular.module("evals", ['angularUtils.directives.dirPagination']);

    var webauthUser = null;
    var memberInfo = null;

    /*
    Services
     */

    // EvalsAPI - service for making Ajax requests to the EvalsAPI
    app.factory("EvalsAPI", ["$http", function($http){
        // API base URL
        var apiUrl = "https://www.csh.rit.edu/~henry/bvals/api/";

        // ajaxSuccess() - fires appropriate AJAX callback based on response status
        var ajaxSuccess = function (cbPass, cbFail) {
            return function (resp) {
                
                cbPass(resp);
            };
        };

        // ajaxError() - handle AJAX errors
        var ajaxError = function (e) {
            console.error(e);
        };

        // Service object
        return {
            getMemberInfo: function (username, pass, fail) {
                $http.get(apiUrl + "getMemberInfo.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getHouseMeetings: function (username, pass, fail) {
                $http.get(apiUrl + "getHouseMeetings.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getAllOnFloorMembers: function (username, pass, fail) {
                $http.get(apiUrl + "getAllOnFloorMembers.php").success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getQueue: function (username, pass, fail) {
                $http.get(apiUrl + "getQueue.php").success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getQueuePosition: function (username, pass, fail) {
                $http.get(apiUrl + "getQueuePosition.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getRoster: function (username, pass, fail) {
                $http.get(apiUrl + "getRoster.php").success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getRoom: function (username, pass, fail) {
                $http.get(apiUrl + "getRoom.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getMajorProjects: function (username, pass, fail) {
                if(username != "") {
                    $http.get(apiUrl + "getMajorProjects.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
                }
                else {
                    $http.get(apiUrl + "getMajorProjects.php").success(ajaxSuccess(pass, fail)).error(ajaxError);
                }
            },
            getSpringEvals: function (username, pass, fail) {
                $http.get(apiUrl + "getSpringEvals.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getFreshmanEvals: function (username, pass, fail) {
                $http.get(apiUrl + "getFreshmanEvals.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            },
            getConditionals: function (username, pass, fail) {
                if(username !== "") {
                    $http.get(apiUrl + "getConditionals.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
                }
                else {
                    $http.get(apiUrl + "getConditionals.php").success(ajaxSuccess(pass, fail)).error(ajaxError);
                }
            },
            getAttendance: function (username, pass, fail) {
                $http.get(apiUrl + "getAttendance.php?user=" + username).success(ajaxSuccess(pass, fail)).error(ajaxError);
            }
            
        };
    }]);

    /*
    Controllers
     */

    app.controller("MemberInfoController", ["$scope", "EvalsAPI", function($scope, EvalsAPI){
        // Hardcoded for now
        // TODO: Webauth integration in getMemberInfo.php
        webauthUser = 'smirabito';

        var HeaderCtrl = this;

        if(memberInfo == null){
            EvalsAPI.getMemberInfo(
                webauthUser,
                function(data){
                     
                    HeaderCtrl.data = data;
                    memberInfo = data;
                },
                false
            );
        } else {
            HeaderCtrl.data = memberInfo;
        }
    }]);
    
    
    app.controller("HousingQueueController", ["$scope", "EvalsAPI", function($scope, EvalsAPI){
        // Hardcoded for now
        // TODO: Webauth integration in getMemberInfo.php
        webauthUser = 'smirabito';

            EvalsAPI.getQueue(
                webauthUser,
                function(data){
                     
                    $scope.data = data;
                    
                },
                false
            );
    }]);
    
    app.controller("OnFloorMembersController", ["$scope", "EvalsAPI", function($scope, EvalsAPI){
        // Hardcoded for now
        // TODO: Webauth integration in getMemberInfo.php
        webauthUser = 'smirabito';
        
            EvalsAPI.getAllOnFloorMembers(
                webauthUser,
                function(data){
                     
                    $scope.data = data;
                    
                },
                false
            );
    }]);
    app.controller("HousingRosterController", ["$scope", "EvalsAPI", function($scope, EvalsAPI){
        // Hardcoded for now
        // TODO: Webauth integration in getMemberInfo.php
        webauthUser = 'smirabito';
        
            EvalsAPI.getRoster(
                webauthUser,
                function(data){
                    console.log(data);                
                    $scope.data = data;
                    $scope.roomFilter = 0;
                    $scope.activeYearValue = 'current';
                    $scope.activeRoomValue = 0;
                    $scope.yearFilter = {year:'current'};
                    $scope.roomFilterController = function (item) { 
                        if($scope.roomFilter == 1){
                            return item.roommate1 == "EMPTY" || item.roommate2 == "EMPTY"; 
                        }
                        else{
                        return true;
                        }
    
};
     
                },
                false
                );
    }]);

    app.controller("EvaluationResultsController", ["$scope", "EvalsAPI", function($scope, EvalsAPI){
        // Hardcoded for now
        // TODO: Webauth integration in getMemberInfo.php
        webauthUser = 'smirabito';

        this.getCommitteeMeetingsForMember = function(uid){
            var member = $.grep($scope.memberInfo, function(e){
                return e.username === uid;
            });

            return member.committee_mtgs;
        };

        this.getHouseMeetingsMissedForMember = function(uid){
            var member = $.grep($scope.houseMeetingsData, function(e){
                return e.username === uid;
            });

            return member.house_meetings_missed;
        };

        if(memberInfo == null){
            EvalsAPI.getMemberInfo(
                "",
                function(data){
                    $scope.memberInfo = memberInfo;
                },
                false
            );
        } else {
            $scope.memberInfo = memberInfo;
        }

        EvalsAPI.getHouseMeetings(
            "",
            function (data) {
                $scope.houseMeetingsData = data;
            },
            false
        );

        if($scope.type == 'freshman') {
            EvalsAPI.getFreshmanEvals(
                "",
                function(data){
                    $scope.evalData = data;
                },
                false
            );
        } else if($scope.type == 'spring') {
            EvalsAPI.getSpringEvals(
                "",
                function(data){
                    $scope.evalData = data;
                },
                false
            );
        } else if($scope.type == 'winter') {
            // TODO: Winter evals API?
        }
    }]);

    /*
     Filters
     */

    app.filter('capitalize', function() {
        return function(input) {
            return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
        }
    });

    /*
     Directives
     */

    app.directive('attendanceWidget', function(){
        return {
            restrict: 'E',
            templateUrl: 'directives/attendance_widget.html',
            controller: ["$scope", "EvalsAPI", function($scope, EvalsAPI){
                var AttendanceCtrl = this;
                this.noData = true;

                EvalsAPI.getAttendance(
                    webauthUser,
                    function(data){
                         
                        AttendanceCtrl.data = data;

                        if(AttendanceCtrl.data.length != 0){
                            AttendanceCtrl.noData = false;
                        }
                    },
                    false
                );
            }],
            controllerAs: 'attendance'
        };
    });

    app.directive('conditionalsWidget', function(){
        return {
            scope: {
                all: '='
            },
            replace: true,
            restrict: 'E',
            templateUrl: 'directives/conditionals_widget.html',
            controller: ["$scope", "EvalsAPI", function($scope, EvalsAPI){
                var ConditionalsCtrl = this;

                this.noData = true;

                EvalsAPI.getConditionals(
                    ($scope.all ? "" : webauthUser),
                    function(data){
                         
                        ConditionalsCtrl.data = data;

                        if(ConditionalsCtrl.data.length != 0){
                            ConditionalsCtrl.noData = false;
                        }
                    },
                    false
                );
            }],
            controllerAs: 'conditionals'
        };
    });

    app.directive('evaluationsWidget', function(){
        return {
            restrict: 'E',
            templateUrl: 'directives/evaluations_widget.html',
            controller: ["$scope", "EvalsAPI", function($scope, EvalsAPI){
                EvaluationsCtrl = this;
                this.isFreshmanEvals = false;
                this.house_meetings_missed = 0;

                if(memberInfo == null){
                    EvalsAPI.getMemberInfo(
                        webauthUser,
                        function(data){
                             
                            memberInfo = data;
                        },
                        false
                    );
                }

                EvalsAPI.getHouseMeetings(
                    webauthUser,
                    function(data){
                         

                        data.forEach(function(meeting){
                            if(!meeting.present){
                                EvaluationsCtrl.house_meetings_missed++
                            }
                        });
                    },
                    false
                );

                EvalsAPI.getFreshmanEvals(
                    webauthUser,
                    function(data){
                         

                        if(data.length == 0){
                            EvalsAPI.getSpringEvals(
                                webauthUser,
                                function(data) {
                                     
                                    EvaluationsCtrl.data = data;
                                    EvaluationsCtrl.data.committee_mtgs = memberInfo.committee_mtgs;
                                    EvaluationsCtrl.data.house_meetings_missed = EvaluationsCtrl.house_meetings_missed;
                                },
                                false
                            );
                        } else {
                            EvaluationsCtrl.isFreshmanEvals = true;
                            EvaluationsCtrl.data = data;
                            EvaluationsCtrl.data.committee_mtgs = memberInfo.committee_mtgs;
                            EvaluationsCtrl.data.house_meetings_missed = EvaluationsCtrl.house_meetings_missed;
                        }
                    },
                    false
                );
            }],
            controllerAs: 'evaluations'
        };
    });

    app.directive('housingWidget', function(){
        return {
            restrict: 'E',
            templateUrl: 'directives/housing_widget.html',
            controller: ["$scope", "EvalsAPI", function($scope, EvalsAPI){
                var HousingCtrl = this;

                this.data = {};
                this.queue = {};

                this.queue.inQueue = true;

                if(memberInfo == null){
                    EvalsAPI.getMemberInfo(
                        webauthUser,
                        function(data){
                            
                            memberInfo = data;
                            HousingCtrl.data.housingPoints = memberInfo.housing_points;
                        },
                        false
                    );
                } else {
                    this.data.housingPoints = memberInfo.housing_points;
                }

                EvalsAPI.getQueuePosition(
                    webauthUser,
                    function(data){
                        
                        HousingCtrl.queue = data;

                        if(HousingCtrl.queue.queuePosition == 0){
                            HousingCtrl.queue.inQueue = false;

                            EvalsAPI.getRoom(
                                webauthUser,
                                function(data){
                                    
                                    HousingCtrl.data = data;
                                    HousingCtrl.data.housingPoints = memberInfo.housing_points;

                                    if (HousingCtrl.data.current.length == 0) {
                                        HousingCtrl.data.current.room_number = "N/A";
                                    }

                                    if (HousingCtrl.data.next.length == 0) {
                                        HousingCtrl.data.next.room_number = "N/A";
                                    }
                                },
                                false
                            );
                        } else {
                            HousingCtrl.queue.inQueue = true;
                        }
                    },
                    false
                );
            }],
            controllerAs: 'housing'
        };
    });

    app.directive('majorProjectsWidget', function(){
        return {
            restrict: 'E',
            scope: {
                all: '='
            },
            templateUrl: 'directives/major_projects_widget.html',
            controller: ["$scope", "EvalsAPI", function($scope, EvalsAPI){
                var ProjectsCtrl = this;

                EvalsAPI.getMajorProjects(
                    ($scope.all ? "" : webauthUser),
                    function(data){
                        
                        ProjectsCtrl.data = data;
                    },
                    false
                );
            }],
            controllerAs: 'majorProjects'
        };
    });
})();