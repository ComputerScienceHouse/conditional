import {Enum} from 'enumify';

export default class ConditionalException {
    constructor(exception, additionalMessage) {
        this.message = "[Conditional] ";

        if (exception instanceof Enum) {
            try {
                this.message += exception.message;
            } catch (e) {
                this.message += exception.name;
            }
        } else {
            try {
                this.message += exception;
            } catch (e) {
                this.message += "Unknown exception"
            }
        }

        if (typeof additionalMessage !== "undefined") {
            this.message += ": " + additionalMessage;
        }
    }

    print() {
        console.error(this.message);
    }
}