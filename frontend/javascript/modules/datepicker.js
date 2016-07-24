import "bootstrap-material-datetimepicker";

export default class DatePicker {
    constructor(input) {
        this.input = input;

        this.render();
    }

    render() {
        window.$(this.input).bootstrapMaterialDatePicker({
            weekStart: 0,
            time: false
        });
    }
}