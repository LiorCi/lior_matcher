from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.state import InstanceState

from matcher import db
from matcher.models import JobCandidateOpinion, JobCandidate, Job, Candidate, \
    CandidateWordTitle, JobWordTitle, CandidateSkill


def candidate_finder(job_id):
    """
    Return all candidate match to job, in this order:
    1. candidate with match title* and skill
    2. candidate with match title will be first,
    3. candidate with no title match only skill match

    * match title- at least one of the words in job title match at least one word in candidate title
    :param job_id: int, job id
    :return: list of order matching candidate
    """

    # get matches
    db_results = db.session.query(Candidate, JobCandidate) \
        .join(JobCandidate) \
        .outerjoin(JobCandidateOpinion) \
        .filter(JobCandidate.job_id == job_id) \
        .order_by(JobCandidate.is_title_match.desc(), JobCandidate.is_skill_match.desc()) \
        .all()

    match_to_update_counter = []
    match_candidate = []
    for db_result in db_results:
        match_to_update_counter.append(db_result.JobCandidate)
        # remove candidate with opinion # TODO do it in left outer join
        if len(db_result.JobCandidate.job_candidate_opinion) == 0:
            match_candidate.append(db_result.Candidate)

    update_match_counter(match_to_update_counter)
    #
    # matches = [db_result.Candidate for db_result in db_results if not len(db_result.JobCandidate.job_candidate_opinion)]
    return match_candidate


def update_match_candidate(job_id):
    """
    update job_candidate db table
    insert or update match candidate
    :param job_id: int, job id
    """

    # get matches by title (at least one title word is the same)
    match_titles = db.session.query(CandidateWordTitle.candidate_id, JobWordTitle.job_id)\
        .filter(CandidateWordTitle.word == JobWordTitle.word, JobWordTitle.job_id == job_id) \
        .all()

    job_candidate_title = [JobCandidate(job_id=match.job_id, candidate_id=match.candidate_id, is_title_match=True)
                           for match in match_titles]
    insert_job_candidate(job_candidate_title)

    match_skills = db.session.query(CandidateSkill.candidate_id, Job.id).filter(CandidateSkill.skill_id == Job.skill_id,
                                                                                Job.id == job_id).all()

    job_candidate_skills = [JobCandidate(job_id=match.id, candidate_id=match.candidate_id, is_skill_match=True) for
                            match in match_skills]
    insert_job_candidate(job_candidate_skills)


def insert_job_candidate(job_candidate_lst):
    # TODO need to do bulk insert or update
    for job_candidate in job_candidate_lst:
        try:
            # create
            db.session.add(job_candidate)
            db.session.commit()
        except IntegrityError:
            # update
            db.session.rollback()
            update_job_candidate = db.session.query(JobCandidate).filter(JobCandidate.job_id == job_candidate.job_id,
                                                                         JobCandidate.candidate_id == job_candidate.candidate_id).first()
            if job_candidate.is_title_match:
                update_job_candidate.is_title_match = job_candidate.is_title_match
            if job_candidate.is_skill_match:
                update_job_candidate.is_skill_match = job_candidate.is_skill_match
            db.session.commit()


def update_match_counter(matches):
    for match in matches:
        match.match_counter += 1
        db.session.commit()


def model_to_dict(model):
    res = {}
    for key, value in vars(model).items():
        if type(value) is InstanceState:
            continue
        if type(value) is datetime:
            res[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            res[key] = value
    return res