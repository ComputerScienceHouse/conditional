import { Enumify } from 'enumify';

export default class MasonryException extends Enumify {
  CANT_FIND_SHARED_SELECTOR = new MasonryException("Unable to find shared selector for Masonry grid items");
  _ = MasonryException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}
