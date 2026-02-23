import { Enumify } from 'enumify';

export default class CmAttendanceException extends Enumify {
  SUBMIT_BEFORE_RENDER = CmAttendanceException("Cannot submit updated attendance before the modal renders.");
  _ = CmAttendanceException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}

