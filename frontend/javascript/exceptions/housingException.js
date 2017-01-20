import {Enum} from 'enumify';

class HousingException extends Enum {
}

HousingException.initEnum({
  SUBMIT_BEFORE_RENDER: {
    get message() {
      return "Cannot submit updated roster before the modal renders.";
    }
  }
});

export default HousingException;
