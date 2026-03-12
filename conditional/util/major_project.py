from sqlalchemy import desc, func

from conditional import db, start_of_year
from conditional.models.models import MajorProject
from conditional.models.models import MajorProjectSkill


def get_project_list():
    proj_list = db.session.query(
        MajorProject.id,
        MajorProject.date,
        MajorProject.uid,
        MajorProject.name,
        MajorProject.tldr,
        MajorProject.time_spent,
        MajorProject.description,
        MajorProject.links,
        MajorProject.status,
        func.array_agg(MajorProjectSkill.skill).label("skills")
    ).outerjoin(MajorProjectSkill,
        MajorProject.id == MajorProjectSkill.project_id
    ).group_by(MajorProject.id
    ).where(MajorProject.date >= start_of_year()
    ).order_by(desc(MajorProject.date), desc(MajorProject.id))

    return proj_list
