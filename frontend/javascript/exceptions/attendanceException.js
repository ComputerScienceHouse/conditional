import { Enumify } from 'enumify';

export default class AttendanceException extends Enumify {
  NO_SRC_ATTRIBUTE = AttendanceException("Unable to find data source for attendance module");
  _ = AttendanceException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}
