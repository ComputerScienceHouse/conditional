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
          $('#createConditional').on('hidden.bs.modal', function() {
            $(e.target).text("Conditionaled").off("click").addClass("disabled");
            $(e.target).next().hide();
          });
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
