import HouseMeetingSearch from "./hmSearch";

export default class IntroductoryProjectSearch extends HouseMeetingSearch {
  constructor(input) {
    super(input);
    HouseMeetingSearch._alreadySelectedFilter = (settings, data, dataIndex) => {
      // Only apply the filter if we're currently searching
      if (typeof settings.oPreviousSearch.sSearch !== "undefined" &&
          settings.oPreviousSearch.sSearch !== "") {
        return !(settings.aoData[dataIndex].anCells[1]
          .querySelector('.dropdown-toggle').dataset.selected === "Passed");
      }

      return true;
    };
  }

  _handleKeyAction() {
    // Set the status of the first visible table row's selector to Passed
    let toggle = this.api.table().body().firstElementChild
      .querySelector(".dropdown-toggle");

    ["btn-success", "btn-danger", "btn-warning"]
      .forEach(classToRemove =>
        toggle.classList.remove(classToRemove));

    const caret = document.createElement('span');
    caret.classList.add('caret');
    toggle.text = "Passed ";
    toggle.appendChild(caret);
    toggle.classList.add("btn-success");
    toggle.dataset.selected = "Passed";
  }
}
