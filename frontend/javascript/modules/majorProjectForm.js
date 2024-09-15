import FetchUtil from "../utils/fetchUtil";

export default class MajorProjectForm {


    constructor(form) {
        this.form = form;
        this.endpoint = '/major_project/submit';
        this.tags_written = false;
        this.tag_keys = ["Enter", "Comma"];
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
            document.getElementsByClassName("placeholder").item(0).remove()
        }
        let txt = input.value.replace(/[^a-zA-Z0-9\+\-\.\# ]/g, ''); // allowed characters list
        if (txt) input.insertAdjacentHTML("beforebegin", '<span class="skill-tag" id=f"ski">' + txt + '</span>');
        let skills = document.getElementsByClassName("skill-tag")
        skills[skills.length - 1].addEventListener('click', e => this.onRemoveTag(e));
        input.value = "";
        input.focus();

    }

    onRemoveTag(e) {
        e.target.remove();
    }

    _submitForm(e) {
        e.preventDefault();

        let skills = [];

        for (const skill in document.getElementsByClassName('span[class=skill-tag]')) {
            skills.push(skill.innerText)
        }

        let payload = {
            projectName: this.form.querySelector('input[name=name]').value,
            projectTldr: this.form.querySelector('input[name=tldr]').value,
            projectTimeSpent: this.form.querySelector('textarea[name=time-commitment]').value,
            projectSkills: skills,
            projectDescription: this.form.querySelector('textarea[name=description]').value
        };

        FetchUtil.postWithWarning(this.endpoint, payload, {
            warningText: "You will not be able to edit your " +
                "project once it has been submitted.",
            successText: "Your project has been submitted."
        });
    }
}
