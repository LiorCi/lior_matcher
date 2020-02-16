import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT

from matcher import db


class Skill(db.Model):
    __tablename__ = 'skill'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

    job = db.relationship('Job', backref='skill', lazy=True)
    candidate_skill = db.relationship('CandidateSkill', backref='Skill', lazy=True)

    def __repr__(self):
        return self.name


class Candidate(db.Model):
    __tablename__ = 'candidate'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)

    candidate_skill = db.relationship('CandidateSkill', backref='Candidate', lazy=True)
    job_candidate = db.relationship('JobCandidate', backref='Candidate', lazy=True)

    def __repr__(self):
        return 'id {}'.format(self.id)


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(256), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'),  nullable=False)

    job_candidate = db.relationship('JobCandidate', backref='job', lazy=True)

    def __repr__(self):
        return 'id {}'.format(self.id)


class CandidateSkill(db.Model):
    __tablename__ = 'candidate_skill'

    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), primary_key=True,  nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return 'id {}'.format(self.id)


class JobCandidate(db.Model):
    __tablename__ = 'job_candidate'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    match_counter = db.Column(db.Integer, default=0)
    is_title_match = db.Column(TINYINT)
    is_skill_match = db.Column(TINYINT)

    __table_args__ = (UniqueConstraint('job_id', 'candidate_id', name='_job_candidate_uc'),)

    job_candidate_opinion = db.relationship('JobCandidateOpinion', backref='JobCandidate', lazy=True)
    job_candidate_notes = db.relationship('JobCandidateNote', backref='JobCandidate', lazy=True)

    def __repr__(self):
        return 'id {}'.format(self.id)


class JobCandidateOpinion(db.Model):
    __tablename__ = 'job_candidate_opinion'

    id = db.Column(db.Integer, primary_key=True)
    job_candidate = db.Column(db.Integer, db.ForeignKey('job_candidate.id'))
    opinion = db.Column(db.String(256), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False,  default=datetime.datetime.utcnow)

    def __repr__(self):
        return 'id {}'.format(self.id)


class JobCandidateNote(db.Model):
    __tablename__ = 'job_candidate_note'

    id = db.Column(db.Integer, primary_key=True)
    job_candidate = db.Column(db.Integer, db.ForeignKey('job_candidate.id'))
    note = db.Column(db.String(256), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False,  default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<id {}>'.format(self.id)


class JobWordTitle(db.Model):
    _tablename_ = 'job_word_title'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    word = db.Column(db.String(256), nullable=False)


class CandidateWordTitle(db.Model):
    _tablename_ = 'candidate_word_title'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    word = db.Column(db.String(256), nullable=False)


