import { Enumify } from 'enumify';

export default class FetchException extends Enumify {
  REQUEST_FAILED = new FetchException("Unable to retrieve data from server");
  _ = FetchException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}
