import { Enumify } from 'enumify';

export default class HmSearchException extends Enumify {
  TARGET_REQUIRED = HmSearchException("A target selector is required to use HouseMeetingSearch");
  NOT_A_TABLE = HmSearchException("The HouseMeetingSearch module requires the target to be a table");
  _ = HmSearchException.closeEnum();

  constructor(message) {
    super()
    this.message = message;
  }
}
