import FetchUtil from "../utils/fetchUtil";

const CACHE_KEY = "majorProjectCache"

export default class MajorProjectForm {

    constructor(form) {
        this.form = form;
        this.endpoint = '/major_project/submit';
        this.tags_written = false;
        this.tag_keys = ["Enter", "Comma", "Tab"];
	this.saveState;
	try {
	    this.saveState = JSON.parse(localStorage.getItem(CACHE_KEY));
	} catch (e) {
	    console.error(e)
	}
        this.render();
    }

    render() {
        this.form.querySelector('input[type=submit]')
            .addEventListener('click', e => this._submitForm(e));
        this.form.querySelector('input[id=skill-input]')
            .addEventListener('focusout', e => this.onWriteSkill(e));
        this.form.querySelector('input[id=skill-input]')
            .addEventListener('keypress', e => this.onKeyPress(e));
	this.form.addEventListener('input', e => this.onInput());
	if (this.saveState) {
	    for (const [key, value] of Object.entries(this.saveState)) {
		if (key === 'skill-list') {
		    value.forEach((skill) => this.addSkill(skill));
		    this.tags_written = true;
		    continue;
		}
	        this.form.querySelector(`*[name=${key}]`).value = value;
	    }
	}
    }

    onInput() {
        const formData = new FormData(this.form);
        const formDataObject = Object.fromEntries(formData.entries());
	formDataObject['skill-list'] = this.getSkills();
	localStorage.setItem(CACHE_KEY, JSON.stringify(formDataObject));
    }


    onKeyPress(e) {
        if (this.tag_keys.includes(e.code)) {
            e.preventDefault();
            this.onWriteSkill(e);
        }
        return false;
    }

    getSkills() {
	let skills = [];

        for (const tag of this.form.getElementsByClassName('skill-tag')) {
            skills.push(tag.textContent);
        }

	return skills;
    }

    addSkill(skill) {
        let input = document.getElementById("skill-input")
        let txt = skill.replaceAll(/[^a-zA-Z0-9\+\-\.\# ]/g, ''); // allowed characters Skillslist
        if (txt) input.insertAdjacentHTML("beforebegin", '<span class="skill-tag" id=f"ski">' + txt + '</span>');
        let skills = this.form.getElementsByClassName("skill-tag")
        skills.item(skills.length - 1).addEventListener('click', e => this.onRemoveTag(e));
    }

    onWriteSkill(e) {
        let input = document.getElementById("skill-input")
        if (!this.tags_written) {
            this.tags_written = true

            const firstTag = document.getElementsByClassName("skill-tag").item(0);
            if (firstTag) firstTag.remove();
        }
        this.addSkill(input.value);
        input.value = "";
	this.onInput()

    }

    onRemoveTag(e) {
        e.target.remove();
        this.onInput();
    }

    clearForm() {
        const skills = this.form.getElementsByClassName("skill-tag");
        Array.from(skills).forEach(tag => tag.remove());
        for (const [key, value] of Object.entries(this.saveState)) {
	    if (key === 'skill-list') {
		// We already cleaned the skills ^^
		continue;
	    }
	    this.form.querySelector(`*[name=${key}]`).value = "";
	}
	this.tags_written = false;
        localStorage.removeItem(CACHE_KEY);
    }


    _submitForm(e) {
        e.preventDefault();

        const skills = this.getSkills();


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
        }, () => this.clearForm());
    }
}
