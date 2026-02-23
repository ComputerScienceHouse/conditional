import { Enumify } from 'enumify';

export default class ConditionalException extends Error {
  constructor(exception, additionalMessage) {
    let message = "";

    if (exception instanceof Enumify) {
      try {
        message += exception.message;
      } catch (e) {
        message += exception.name;
      }
    } else {
      try {
        message += exception;
      } catch (e) {
        message += "An unknown error has occured";
      }
    }

    if (additionalMessage) {
      message += ": " + additionalMessage;
    }

    super(message);
    this.name = "ConditionalException";
    this.message = message;
  }
}
