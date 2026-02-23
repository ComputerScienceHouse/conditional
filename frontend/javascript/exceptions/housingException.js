import { Enumify } from 'enumify';

export default class HousingException extends Enumify {
  SUBMIT_BEFORE_RENDER = HousingException("Cannot submit updated roster before the modal renders.");
  _ = HousingException.closeEnum();

  constructor(message) {
    super();
    this.message = message;
  }
}
