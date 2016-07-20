export default class FrequencyMap {
    // Babel doesn't support extending native objects, so just wrap it
    constructor() {
        this.map = new Map();
    }

    has(key) {
        return this.map.has(key);
    }

    get(key) {
        return this.map.get(key);
    }

    set(key, value) {
        return this.map.set(key, value);
    }

    entries() {
        return this.map.entries();
    }

    increment(key) {
        if (this.has(key)) {
            this.set(key, this.get(key) + 1);
        } else {
            this.set(key, 1);
        }
    }

    getHighest() {
        let highestFreq = 0;
        let highestKey = null;

        for (let [key, freq] of this.entries()) {
            if (freq > highestFreq) {
                highestKey = key;
                highestFreq = freq;
            }
        }

        return highestKey;
    }
}