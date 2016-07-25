import {Enum} from 'enumify';

class AttendanceException extends Enum {
}

AttendanceException.initEnum({
    'NO_SRC_ATTRIBUTE': {
        get message() {
            return "Unable to find data source for attendance module";
        }
    }
});

export default AttendanceException;