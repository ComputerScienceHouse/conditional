/* global $ */
import Exception from "../exceptions/exception";
import HmSearchException from "../exceptions/hmSearchException";

export default class HouseMeetingSearch {
    constructor(input) {
        this.input = input;
        this.target = document.querySelector(this.input.dataset.target);
        
        if (this.target === null) {
            throw new Exception(HmSearchException.TARGET_REQUIRED);
        } else if (this.target.tagName !== "TABLE") {
            throw new Exception(HmSearchException.NOT_A_TABLE)
        } else {
            // Is the target a DataTable?
            if (typeof $.fn.dataTable !== "undefined" && $.fn.dataTable.isDataTable(this.target)) {
                // Yes, render
                this.render();
            } else {
                // No, wait until it initializes before rendering
                // Must use jQuery to listen - native events aren't fired by DataTables
                $(this.target).on("init.dt", () => this.render());
            }
        }
    }
    
    render() {
        // Remove the event listner so this module doesn't try to render again
        $(this.target).off("init.dt");
        
        // Add custom filtering function
        $.fn.dataTable.ext.search.push(HouseMeetingSearch._alreadySelectedFilter);
        
        // Retrieve the target's DataTable API object
        this.api = $(this.target).DataTable({
            retrieve: true
        });

        // Bind to the input
        this.input.addEventListener("keydown", (event) => this._handleInteraction(event));
    }
    
    _handleInteraction(event) {
        // Did the user press enter?
        var keyCode = event.keyCode || event.which;
        if (keyCode === 13) {
            // Yes, prevent form submission
            event.preventDefault();
            
            // Toggle the first visible table row's checkbox
            HouseMeetingSearch._toggleCheckbox(this.api.table().body().firstElementChild.querySelector("input[type=checkbox]"));
            
            // Reset the table
            this.api.search('').draw();
            
            // Clear and refocus input
            this.input.value = "";
            this.input.focus();
        } else {
            // No, search and redraw the table
            this.api.search(this.input.value).draw();
        }
    }
    
    /*
     * Custom filtering function that will remove rows that are already selected
     */
    static _alreadySelectedFilter(settings, data, dataIndex) {
        // Only apply the filter if we're currently searching
        if (typeof settings.oPreviousSearch.sSearch !== "undefined" && settings.oPreviousSearch.sSearch !== "") {
            return settings.aoData[dataIndex].anCells[1].querySelector("input[type=checkbox]").checked ? false : true;
        }
        
        return true;
    }
    
    /*
     * Checkbox toggle helper
     */
    static _toggleCheckbox(checkbox) {
        checkbox.checked ? checkbox.checked = false : checkbox.checked = true;
    }
}