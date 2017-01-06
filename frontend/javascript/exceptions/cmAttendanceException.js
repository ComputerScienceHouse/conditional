import {Enum} from 'enumify';

class CmAttendanceException extends Enum {
}

CmAttendanceException.initEnum({
  SUBMIT_BEFORE_RENDER: {
    get message() {
      return "Cannot submit updated attendance before the modal renders.";
    }
  }
});

export default CmAttendanceException;
