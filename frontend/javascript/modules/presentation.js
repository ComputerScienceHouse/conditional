import FetchUtil from '../utils/fetchUtil';
import reveal from 'reveal.js';
export default class Presentation {
  constructor(element) {
    this.element = element;
    if (location.pathname.split('/')[2] === "intro") {
      this.endpoint = '/slideshow/intro/review';
    } else {
      this.endpoint = '/slideshow/spring/review';
    }
    this.render();
  }
  render() {
    reveal.initialize();

    const name = $('h1.member-name');
    const nameHeight = name.height();
    const nameLineheight = parseFloat(name.css('line-height'));
    const nameRows = nameHeight / nameLineheight; // get # lines of name elem
    if (nameRows > 1) { // if name wraps to two lines
      name.css('font-size', '1.5em');
    }

    $('.reveal button.pass').click(e => {
      let uid = e.target.parentElement.dataset.uid; // Ex: ID of 'pass-ram' => 'ram'
      let cn = e.target.parentElement.dataset.cn;
      e.preventDefault();
      let payload = {
        uid: uid,
        status: "Passed"
      };
      FetchUtil.postWithWarning(this.endpoint, payload, {
        warningText: "Are you sure you want to pass " + cn + "?",
        successText: cn + " has been marked as passed."
      }, () => {
        $(e.target).text("Passed").off("click").addClass("disabled");
        $(e.target).next().hide();
        reveal.right();
      });
    });
    $('.reveal button.fail').click(e => {
      let uid = e.target.parentElement.dataset.uid; // Ex: ID of 'pass-ram' => 'ram'
      let cn = e.target.parentElement.dataset.cn;
      $(e.target).prev()
        .removeClass('pass')
        .addClass('conditional')
        .text('Conditional')
        .attr("id", "conditional-" + uid)
        .off('click')
        .click(e => {
          $('#createConditional').modal();
          $('#createConditional input[type="text"]').val('');
          $('#createConditional input[name="uid"]').val(uid);
        });
      $(e.target).click(e => {
        e.preventDefault();
        let payload = {
          uid: uid,
          status: "Failed"
        };
        FetchUtil.postWithWarning(this.endpoint, payload, {
          warningText: "Are you sure you want to fail " + cn + "?",
          successText: cn + " has been marked as failed."
        }, () => {
          $(e.target).text("Failed").off("click").addClass("disabled");
          $(e.target).prev().hide();
          reveal.right();
        });
      });
    });
  }
}
