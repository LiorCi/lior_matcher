from flask_admin.contrib.sqla import ModelView

from matcher.models import JobWordTitle, CandidateWordTitle
from matcher import db


class JobMV(ModelView):
    form_columns = ('title', 'status', 'skill')
    column_display_pk = True

    def after_model_change(self, form, model, is_created):
        if is_created is False:
            JobWordTitle.query.filter_by(job_id=model.id).delete()

        title = form.data.get('title')
        self._create_splited_title(title, model.id)

    def on_model_change(self, form, model, is_created):
        model.title = model.title.lower()
        model.status = model.status.lower()

    def _create_splited_title(self, title, model_id):
        if title:
            title_words_arr = title.split()
            for word in title_words_arr:
                job_word_title = JobWordTitle(job_id=model_id, word=word)
                db.session.add(job_word_title)
            db.session.commit()


class CandidateMV(ModelView):
    form_columns = ('title',)
    column_display_pk = True

    def after_model_change(self, form, model, is_created):

        if is_created is False:
            CandidateWordTitle.query.filter_by(candidate_id=model.id).delete()

        title = form.data.get('title')
        self._cretae_splited_title(title, model.id)

    def on_model_change(self, form, model, is_created):
        model.title = model.title.lower()

    def _cretae_splited_title(self, title, model_id):
        if title:
            title_words_arr = title.split()
            for word in title_words_arr:
                candidate_word_title = CandidateWordTitle(candidate_id=model_id, word=word)
                db.session.add(candidate_word_title)
            db.session.commit()


class SkillMV(ModelView):
    form_columns = ('name', )

    def on_model_change(self, form, model, is_created):
        model.name = model.name.lower()


class CandidateSkillMW(ModelView):
    pass
