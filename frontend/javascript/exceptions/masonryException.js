import {Enum} from 'enumify';

class MasonryException extends Enum {
}

MasonryException.initEnum({
  CANT_FIND_SHARED_SELECTOR: {
    get message() {
      return "Unable to find shared selector for Masonry grid items";
    }
  }
});

export default MasonryException;
