import Exception from "../exceptions/exception";
import FetchException from "../exceptions/fetchException";

export default class FetchUtil {
    static checkStatus(response) {
        if (response.status >= 200 && response.status < 300) {
            return response;
        } else {
            throw new Exception(FetchException.REQUEST_FAILED, "received response code " + response.status);
        }
    }
    
    static parseJSON(response) {
        return response.json();
    }
}