# DB Models #

## FreshmanAccount table ##
This table stores the basic metadata associated with a freshman before they pass
their 10-week evaluation.
* `id`: Autoincrementing primary key.
* `name`: The freshman's name
* `eval_date`: The date of the freshman's 10-week evaluation

## FreshmanEvalData table ##
This table stores the evaluations data for freshmen before they pass their
10-week evaluations.
* `id`: Autoincrementing primary key.
* `uid`: The freshman's LDAP uid (if they pass their packet)
* `freshman_project`: Their status on the freshman project (pending, passed,
  failed)
* `signatures_missed`: The number of signatures the freshman missed.
* `social_events`: The social events the freshman attended (part of the fall
  evals form)
* `other_notes`: Any other notes the freshman has attended (part of the fall
  evals form)

## CommitteeMeeting table ##
This table stores a list of committee meetings.
* `id`: Autoincrementing primary key.
* `committee`: The committee the meeting belongs to.
* `timestamp`: The date and time of the meeting.
* `active`: Whether the meeting applies to the current year or not.

## MmeberCommitteeAttendance table ##
This table stores attendance for committee meetings for full members (i.e.
non-freshmen).
* `id`: Autoincrementing primary key.
* `uid`: The LDAP uid (i.e. username) of the member who attended the meeting
* `meeting_id`: Foreign key referencing the meeting that was attended
  (`committee_meetings.id`)

## FreshmanCommitteeAttendance table ##
This table stores attendance for committee meetings for freshmen.
* `id`: Autoincrementing primary key.
* `fid`: Foreign key referencing the freshman account for the freshman who
  attended (`freshman_accounts.id`).
* `meeting_id`: Foreign key referencing the meeting that was attended
  (`committee_meetings.id`)

## TechnicalSeminar table ##
This table stores a list of technical seminars.
* `id`: Autoincrementing primary key.
* `name`: The name of the seminar
* `active`: Whether or not the seminar applies to the current year.

## MemberSeminarAttendance table ##
Stores seminar attendance for full members.
* `id`: Autoincrementing primary key.
* `uid`: The LDAP uid of the member who atended the seminar
* `seminar_id`: Foreign key referencing the seminar attended
  (`technical_seminars.id`)

## FreshmanSeminarAttendance table ##
Stores seminar attendance for freshmen.
* `id`: Autoincrementing primary key.
* `fid`: Foreign key referencing the freshman who attended the seminar
  (`freshman_accounts.id`)
* `meeting_id`: Foreign key referencing the seminar attended
  (`technical_seminars.id`)

## MajorProject table ##
Stores major projects through their entire lifetime.
* `id`: Autoincrementing primary key.
* `uid`: LDAP uid of the member the project belongs to
* `name`: Name of the major project
* `description`: Description of the project
* `status`: Status of the project (pending, passed, failed)

## HouseMeeting table ##
Stores occurrences of house meeting.
* `id`: Autoincrementing primary key.
* `date`: Date the meeting occurred
* `active`: Whether or not the meeting applies to the current year

## MemberHouseMeetingAttendance table ##
Stores house meeting attendance data for full members. If a member does not have
an entry for a given house meeting, that means they were not required to attend
that house meeting.
* `id`: Autoincrementing primary key.
* `uid`: LDAP uid of the member the attendance record is for
* `meeting_id`: Foreign key referencing the house meeting attended
  (`house_meetings.id`)

## FreshmanHouseMeetingAttendance table ##
Stores house meeting attendance data for freshmen.
* `id`: Autoincrementing primary key.
* `fid`: Foreign key referencing the freshman the attendance record is for
  (`freshman_accounts.id`)
* `meeting_id`: Foreign key referencing the house meeting attended
  (`house_meetings.id`)

## CurrentCoops table ##
Used to store members who are inactive and on co-op, to distinguish them from
members who are inactive but could potentially become active later in the
semester/year.
* `id`: Autoincrementing primary key.
* `username`: LDAP uid of the member on coop.
