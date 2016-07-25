import {Enum} from 'enumify';

class FetchException extends Enum {
}

FetchException.initEnum({
    'REQUEST_FAILED': {
        get message() {
            return "Unable to retrieve data from server";
        }
    }
});

export default FetchException;