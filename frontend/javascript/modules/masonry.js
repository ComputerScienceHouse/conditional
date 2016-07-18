require("simple-masonry");
import FreqencyMap from "../models/frequencyMap";
import Exception from "../exceptions/exception";
import MasonryException from "../exceptions/masonryException";

export default class MasonryLayout {
    constructor(grid) {
        this.grid = grid;
    }

    _findSharedSelector() {
        let selectors = new FreqencyMap();
        let sharedSelector = null;

        try {
            this.grid.childNodes.forEach((child) => {
                if (typeof child.id !== "undefined" && child.id !== null && child.id !== "") {
                    selectors.increment("#" + child.id);
                }

                if (typeof child.className !== "undefined" && child.className !== null && child.className !== "") {
                    child.className.split(/\s+/).forEach((className) => {
                        selectors.increment("." + className);
                    });
                }
            });

            sharedSelector = selectors.getHighest();
        } catch (e) {
            throw new Exception(MasonryException.CANT_FIND_SHARED_SELECTOR, e.message);
        }

        if (sharedSelector !== null) {
            return sharedSelector;
        } else {
            throw new Exception(MasonryException.CANT_FIND_SHARED_SELECTOR);
        }
    }
}