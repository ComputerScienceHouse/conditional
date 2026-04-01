import FetchUtil from "../utils/fetchUtil";

export default class MajorProjectForm {


    constructor(form) {
        this.form = form;
        this.endpoint = '/major_project/submit';
        this.tags_written = false;
        this.tag_keys = ["Enter", "Comma", "Tab"];
        this.render();
    }

    render() {
        this.form.querySelector('input[type=submit]')
            .addEventListener('click', e => this._submitForm(e));
        this.form.querySelector('input[id=skill-input]')
            .addEventListener('focusout', e => this.onWriteSkill(e));
        this.form.querySelector('input[id=skill-input]')
            .addEventListener('keypress', e => this.onKeyPress(e));
    }

    onKeyPress(e) {
        if (this.tag_keys.includes(e.code)) {
            e.preventDefault();
            this.onWriteSkill(e);
        }
        return false;
    }

    onWriteSkill(e) {
        let input = document.getElementById("skill-input")
        if (!this.tags_written) {
            this.tags_written = true

            const firstTag = document.getElementsByClassName("skill-tag").item(0);
            if (firstTag) firstTag.remove();
        }
        
        let txt = input.value.replaceAll(/[^a-zA-Z0-9\+\-\.\# ]/g, ''); // allowed characters list
        if (txt) input.insertAdjacentHTML("beforebegin", '<span class="skill-tag" id=f"ski">' + txt + '</span>');
        let skills = this.form.getElementsByClassName("skill-tag")
        skills.item(skills.length - 1).addEventListener('click', e => this.onRemoveTag(e));
        input.value = "";
    }

    onRemoveTag(e) {
        e.target.remove();
    }

    _submitForm(e) {
        e.preventDefault();

        let skills = [];

        for (const tag of this.form.getElementsByClassName('skill-tag')) {
            skills.push(tag.textContent);
        }
        
        let projectName = this.form.querySelector('input[name=name]').value;
        let projectTldr = this.form.querySelector('input[name=tldr]').value;
        let projectTimeSpent = this.form.querySelector('textarea[name=time-commitment]').value;
        let projectDescription = this.form.querySelector('textarea[name=description]').value;
        let projectLinks = this.form.querySelector('textarea[name=links]').value;

        // For each field, if it is not empty, trim it.
        if (projectName !== "") projectName = projectName.trim();
        if (projectTldr !== "") projectTldr = projectTldr.trim();
        if (projectTimeSpent !== "") projectTimeSpent = projectTimeSpent.trim();
        if (projectDescription !== "") projectDescription = projectDescription.trim();

        if (!projectName || !projectTldr || !projectTimeSpent || !projectDescription || skills.length === 0) {
            alert("Error: At least one required field is empty. \n\nProject Name, TLDR, Time Commitment, Description, and at least one skill are required.");
            return;
        }

        let payload = {
            projectName: projectName,
            projectTldr: projectTldr,
            projectTimeSpent: projectTimeSpent,
            projectSkills: skills,
            projectDescription: projectDescription,
            projectLinks: projectLinks
        };


        console.log(payload)

        FetchUtil.postWithWarning(this.endpoint, payload, {
            warningText: "You will not be able to edit your " +
                "project once it has been submitted.",
            successText: "Your project has been submitted."
        });
    }
}