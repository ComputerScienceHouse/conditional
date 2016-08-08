$(function () {
    // Existing autofill detection doesn't check textareas
    $("textarea").each(function () {
        var $this = $(this);
        if ($this.val() && $this.val() !== $this.attr("value")) {
            $this.trigger("change");
        }
    });
});