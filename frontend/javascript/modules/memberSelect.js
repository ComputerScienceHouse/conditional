/* global fetch */
import "whatwg-fetch";
import Choices from "choices.js";
import FetchUtil from "../utils/fetchUtil";
import Exception from "../exceptions/exception";
import AttendanceException from "../exceptions/attendanceException";
import FetchException from "../exceptions/fetchException";

export default class MemberSelect {
  constructor(element) {
    this.element = element;
    this.dataSrc = element.dataset.src;

    if (this.dataSrc) {
      fetch('/attendance/' + this.dataSrc, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      })
        .then(FetchUtil.checkResponse)
        .then(FetchUtil.parseJSON)
        .then(response => {
          this.members = response.members;
          this.render(element);
        })
        .catch(error => {
          throw new Exception(FetchException.REQUEST_FAILED, error);
        });
    } else {
      throw new Exception(AttendanceException.NO_SRC_ATTRIBUTE);
    }
  }

  render(element) {
    const target = new Choices(element, {
      choices: this.members,
      removeItemButton: true,
      searchFloor: -1,
      searchRenderSelectedChoices: false,
      resetScrollPosition: true,
      classNames: {
        containerOuter: ['choices', 'dropdown'],
        containerInner: ['_choices__inner', 'form-control'],
        input: ['choices__input', 'form-control-sm', 'border-0'],
        inputCloned: ['choices__input--cloned'],
        list: ['choices__list'],
        listItems: ['choices__list--multiple'],
        listSingle: ['choices__list--single'],
        listDropdown: ['choices__list--dropdown', 'dropdown-menu'],
        item: ['choices__item'],
        itemSelectable: ['choices__item--selectable'],
        itemDisabled: ['choices__item--disabled', 'disabled'],
        itemChoice: ['choices__item--choice', 'dropdown-item'],
        description: ['choices__description'],
        placeholder: ['choices__placeholder'],
        group: ['choices__group'],
        groupHeading: ['choices__heading', 'dropdown-header'],
        button: ['choices__button', 'btn-close'],
        activeState: ['is-active'],
        focusState: ['is-focused'],
        openState: ['is-open'],
        disabledState: ['is-disabled'],
        highlightedState: ['is-highlighted', 'active'],
        selectedState: ['is-selected'],
        flippedState: ['is-flipped'],
        loadingState: ['is-loading'],
        invalidState: ['is-invalid'],
        notice: ['choices__notice'],
        addChoice: ['choices__item--selectable', 'add-choice'],
        noResults: ['has-no-results', 'text-muted'],
        noChoices: ['has-no-choices', 'text-muted'],
      }
    });

    element.addEventListener('addItem', () => {
      requestAnimationFrame(() => {
        target.choiceList.element.scrollTop = 0;
      });
    });

    target.containerOuter.element.addEventListener('keydown', event => {
      // only make tab do stuff if it's actually tab and the dropdown is donw
      // otherwise people will get angryyyy
      if (event.key != "Tab") return;
      if (!target.dropdown.isActive) return;

      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true,
        cancelable: true,
      });

      target.containerOuter.element.dispatchEvent(enterEvent);

      event.preventDefault();
    });

    return target;
  }
}
