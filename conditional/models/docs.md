# DB Models #

## FreshmanAccounts table ##
This table stores the basic metadata associated with a freshman before they pass their 10-week evaluation.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `name`  | `VARCHAR(64)`  | The freshman's name.
| `eval_date` | `DATE` | The date of the freshman's 10-week evaluation.
| `onfloor_status` | `BOOLEAN` | Tracks whether they have been granted on-floor status.
| `signatures_missed` | `INTEGER` | Allows for members who do not get an account to have their missed signatures tracked.

## FreshmanEvalData table ##
This table stores the evaluations data for freshmen before they pass their 10-week evaluations.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | The freshman's LDAP uid (if they pass their packet).
| `freshman_project` | `ENUM` | Their status on the freshman project (`Pending`, `Passed`, `Failed`)
| `signatures_missed` | `INTEGER` | The number of signatures the freshman missed.
| `social_events` | `TEXT` | The social events the freshman attended.
| `other_notes` | `TEXT` | Any other notes the freshman entered into the form.
| `freshman_eval_result` | `ENUM` | The result of introductory evaluations. (`Pending`, `Passed`, `Failed`)
| `active` | `BOOLEAN` | Determines whether the freshman account is currently active / displayed.


## CommitteeMeetings table ##
This table stores a list of committee meetings.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `committee` | `ENUM` | The committee the meeting belongs to.
| `timestamp` | `TIMESTAMP` | The date and time of the meeting.
| `active` | `BOOLEAN` | Whether the meeting applies to the current year or not.

## MemberCommitteeAttendance table ##
This table stores attendance for committee meetings for full members (i.e.
non-freshmen).

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | The LDAP uid (i.e. username) of the member who attended the meeting.
| `meeting_id` | `INTEGER` | Foreign key referencing the meeting that was attended (`committee_meetings.id`).

## FreshmanCommitteeAttendance table ##
This table stores attendance for committee meetings for freshmen.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `fid` | `INTEGER` | Foreign key referencing the freshman account for the freshman who attended (`freshman_accounts.id`).
| `meeting_id` | `INTEGER` | Foreign key referencing the meeting that was attended (`committee_meetings.id`).


## TechnicalSeminar table ##
This table stores a list of technical seminars.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `name` | `VARCHAR(128)` | The name of the technical seminar.
| `active` | `BOOLEAN` | Whether or not the seminar applies to the current year.

## MemberSeminarAttendance table ##
Stores seminar attendance for full members.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | The LDAP uid of the member who attended the seminar.
| `seminar_id` | `INTEGER` | Foreign key referencing the seminar attended (`technical_seminars.id`).

## FreshmanSeminarAttendance table ##
Stores seminar attendance for freshmen.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `fid` | `INTEGER` | Foreign key referencing the freshman who attended the seminar (`freshman_accounts.id`).
| `meeting_id` | `INTEGER` | Foreign key referencing the meeting that was attended (`committee_meetings.id`).

## MajorProject table ##
Stores major projects through their entire lifetime.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | LDAP uid of the member the project belongs to.
| `name` | `VARCHAR(64)` | Name of the major project.
| `description` | `TEXT` |  Description of the project.
| `status` | `ENUM` | Status of the project (`Pending`, `Passed`, `Failed`).
| `active` | `BOOLEAN` | Determines if the project is relevent to the current evaluations period.

## HouseMeeting table ##
Stores occurrences of house meeting.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `date` | `DATE` | Date the meeting occurred.
| `active` | `BOOLEAN` | Whether or not the meeting applies to the current year.

## MemberHouseMeetingAttendance table ##
Stores house meeting attendance data for full members. If a member does not have an entry for a given house meeting, that means they were not required to attend
that house meeting.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | LDAP uid of the member the attendance record is for.
| `meeting_id` | `INTEGER` | Foreign key referencing the house meeting attended (`house_meetings.id`).
| `excuse` | `TEXT` | Reason for not attending.
| `attendance_status` | `ENUM` | Differenciates between storing an `Absent`, `Excused`, or `Present` status.

## FreshmanHouseMeetingAttendance table ##
Stores house meeting attendance data for freshmen.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `fid` | `INTEGER` | Foreign key referencing the freshman the attendance record is for (`freshman_accounts.id`).
| `meeting_id` | `INTEGER` | Foreign key referencing the house meeting attended (`house_meetings.id`).
| `excuse` | `TEXT` | Reason for not attending.
| `attendance_status` | `ENUM` | Differenciates between storing an `Absent`, `Excused`, or `Present` status.

## CurrentCoops table ##
Used to store members who are inactive and on co-op, to distinguish them from members who are inactive but could potentially become active later in the semester/year.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id`  | `INTEGER`  | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | LDAP uid of the member on coop.
| `active` | `BOOLEAN` | Is the co-op still in progress?

## OnFloorStatusAssigned table ##
When members are granted on-floor status plays a role in how they are ranked in the housing queue, making it important to store this information.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `uid` | `VARCHAR(32)` | LDAP uid of the member.
| `onfloor_granted` | `TIMESTAMP` | Date of on-floor vote.


## Conditional table ##
Conditional, so we can store conditionals on Conditional.


|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id` | `INTEGER` | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | LDAP uid of the member in the conditional.
| `date_created` | `TIMESTAMP` | Date conditional assigned.
| `date_due` | `TIMESTAMP` | Date conditional has to be completed by.
| `active` | `BOOLEAN` | Whether or not the conditional is currently relevent. 
| `status` | `ENUM` | Current completion status of the task assigned.

## SpringEval table ##
Records the yearly results of member's spring evaluations.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `id` | `INTEGER` | Autoincrementing primary key.
| `uid` | `VARCHAR(32)` | LDAP uid of the member being evaluated.
| `active` | `BOOLEAN` | Is this evaluation for the current year?
| `date_created` | `TIMESTAMP` | The date of the evaluation.
| `status` | `ENUM` | Result of the evaluation.

## InHousingQueue table ##
Records the yearly results of member's spring evaluations.

|     Field     |      Type     |     Description     |
| ------------- | ------------- | ------------------- |
| `uid` | `VARCHAR(32)` | LDAP uid of the member in the housing queue.


### Member state ###
* Not in LDAP Current Student group: 
  * Alumni. Don't track attendance.
* In LDAP Current Student group and in Co-Op Table: 
  * On coop. Track committee
  meeting attendance, but not house meeting.
* In LDAP Current Student group but not in LDAP Active Group: 
  * Present but not active
  yet. Track attendance as normal.
* In LDAP Current Student group and in LDAP Active group: 
  * Active member. Track attendance as normal.
* In LDAP Active group but not in LDAP Current Student Group: 
  * Invalid. Should not occur.
