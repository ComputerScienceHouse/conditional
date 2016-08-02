import {Enum} from 'enumify';

class HmSearchException extends Enum {
}

HmSearchException.initEnum({
    'TARGET_REQUIRED': {
        get message() {
            return "A target selector is required to use the HouseMeetingSearch module";
        }
    },
    'NOT_A_TABLE': {
        get message() {
            return "The HouseMeetingSearch module requires the target to be a table";
        }
    }
});

export default HmSearchException;