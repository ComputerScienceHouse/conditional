/*
 Automatically instantiates modules based on data-attributes specifying module file-names.
 */

const moduleElements = document.querySelectorAll('[data-module]');

for (let i = 0; i < moduleElements.length; i++) {
  const el = moduleElements[i];
  const name = el.getAttribute('data-module');
  const Module = require(`./${name}`).default;
  new Module(el); // eslint-disable-line no-new
}

/*
 Usage:
 ======

 html
 ----
 <button data-module="disappear">disappear!</button>

 js
 --
 // modules/disappear.js
 export default class Disappear {
     constructor(el) {
        el.style.display = none
     }
 }
 */
