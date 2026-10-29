import {Enumify} from 'enumify';

export default class AdHocException extends Enumify {
  NO_FOLLOW_ATTRIBUTE = AdHocException(
    'Unable to find follow query selector for adhoc module',
  );
  NO_PARENT_ATTRIBUTE = AdHocException(
    'Unable to find parent element id for adhoc module',
  );
  _ = AdHocException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}
