from flask_admin import Admin

from matcher import create_app, model_view, db, models

if __name__ == '__main__':
    app = create_app()

    # Flask admin
    admin = Admin(app, url=app.config['FLASK_ADMIN_URL'], name='matcher', template_mode='bootstrap3')
    admin.add_view(model_view.JobMV(models.Job, db.session))
    admin.add_view(model_view.CandidateMV(models.Candidate, db.session))
    admin.add_view(model_view.SkillMV(models.Skill, db.session))
    admin.add_view(model_view.CandidateSkillMW(models.CandidateSkill, db.session))

    app.run()













