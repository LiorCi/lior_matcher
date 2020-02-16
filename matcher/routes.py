from flask import current_app as app
from webargs import fields
from webargs.flaskparser import use_args
from sqlalchemy.sql.elements import not_
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from matcher import db
from matcher.models import JobCandidateOpinion, JobCandidate, Job, JobCandidateNote
from matcher.utils import candidate_finder, model_to_dict, update_match_candidate


@app.route('/jobs/<job_id>/candidates/match', methods=['GET'])
def get_job_candidates_match(job_id):
    """
    # 2.5
    Return a json containing the matching candidates for job id (only candidate without opinion)
    if job is not open, return 0 candidate
    :param job_id: int, id of job
    :return: json results, with list of match candidate
    """
    # if not open
    if not Job.query.filter_by(id=job_id, status="open").all():
        return {"results": {"status": "success", "matches": []}}, 200

    update_match_candidate(job_id)
    matches = candidate_finder(job_id)

    # results
    matches_results = []
    for match in matches:
        matches_results.append({"candidate_id": match.id,
                                "candidate_title": match.title
                                })
    return {"results": {"status": "success", "matches": matches_results}}, 200


create_opinion_args = {
    'opinion': fields.Str(missing='like'),
}


@app.route('/jobs/<job_id>/candidates/<candidate_id>/opinions', methods=['POST'])
@use_args(create_opinion_args)
def create_opinion(args, job_id, candidate_id):
    """
    # 2.6
    create opinion on a match job-candidate (like/dislike/...)
    :param args: dict, args in create_opinion_args
    :param job_id: int, id of job
    :param candidate_id: id of candidate_id
    :return: json result
    """
    try:
        opinion = args["opinion"]
        job_candidate = db.session.query(JobCandidate)\
            .filter(JobCandidate.job_id == job_id, JobCandidate.candidate_id == candidate_id)\
            .first()

        job_candidate_opinion = JobCandidateOpinion(job_candidate=job_candidate.id, opinion=opinion)
        db.session.add(job_candidate_opinion)
        db.session.commit()
    except IntegrityError as e:
        return {"results": {"status": "failed", "error": e._message()}}, 403
    return {"results": {"status": "success", "object": model_to_dict(job_candidate_opinion)}}, 200


@app.route('/jobs/<job_id>/candidates/likes', methods=['GET'])
def get_job_candidates(job_id):
    """
    # 2.7
    Get the liked candidates for a job (job_id)
    sorted by time of like
    for each candidate get notes if exist
    If the job is closed, return 0 candidates.
    :param job_id: int, job is
    :return:
    """

    # TODO get Opinion and Note one query
    # get liked opinion, open job
    liked_candidates = db.session.query(JobCandidateOpinion)\
        .join(JobCandidate)\
        .join(Job)\
        .filter(not_(Job.status == "close"), JobCandidate.job_id == job_id, JobCandidateOpinion.opinion == "like")\
        .order_by(JobCandidateOpinion.created_on.asc()).all()

    if not liked_candidates:
        return {"results": []}, 200

    # prepare results dict
    candidate_results = {}
    job_candidate_likes_ids = []
    for candidate in liked_candidates:
        job_candidate_likes_ids.append(candidate.job_candidate)
        candidate_results[candidate.JobCandidate.candidate_id] = {"candidate_id": candidate.JobCandidate.candidate_id,
                                                                  "title": candidate.JobCandidate.Candidate.title,
                                                                  "note": []}
    # get note on job_candidate with likes
    candidates_notes = db.session.query(JobCandidateNote)\
        .join(JobCandidate)\
        .filter(JobCandidate.id.in_(job_candidate_likes_ids)).all()

    # add notes to results
    [candidate_results[candidate_note.JobCandidate.candidate_id]["note"].append(candidate_note.note)
     for candidate_note in candidates_notes]

    return {"results": {"status": "success", "candidates": candidate_results}}, 200


create_note_args = {
    'note': fields.Str(required=True)
}


@app.route('/jobs/<job_id>/candidates/<candidate_id>/notes', methods=['POST'])
@use_args(create_note_args)
def create_note(args, job_id, candidate_id):
    """
    # 2.8
    Create a notes on liked candidates regarding a specific job.
    :param args: dict, args in create_note_args
    :param job_id: int, id of job
    :param candidate_id: id of candidate_id
    :return: json result
    """

    # validate like opinion and job open
    job_candidate_opinion = db.session.query(JobCandidateOpinion.job_candidate)\
        .join(JobCandidate)\
        .join(Job)\
        .filter(Job.status == "open", JobCandidate.job_id == job_id, JobCandidate.candidate_id == candidate_id,
                JobCandidateOpinion.opinion == 'like')\
        .first()

    if not job_candidate_opinion:
        return {"results": {"status": "failed", "error": "bad request"}}, 400

    job_candidate_id = job_candidate_opinion.job_candidate

    # create note
    note = JobCandidateNote(job_candidate=job_candidate_id, note=args['note'])
    db.session.add(note)
    db.session.commit()

    note_dict = model_to_dict(note)
    return {"results": {"status": "success", "object": note_dict}}, 200


@app.route('/jobs/<job_id>/statistics', methods=['GET'])
def get_job_statistics(job_id):
    """
    # 2.9
    get statistics on a job
    1. Number of likes
    2. Number of dislikes
    3. Number of notes per candidate
    4. Number of times a candidate was returned as ״matched״ for a job
    :param job_id: int, job id
    :return: json results with statistics
    """
    # number of like/dislike for job
    job_opinions = db.session.query(JobCandidateOpinion.opinion.label("opinion"), func.count(JobCandidateOpinion.opinion).label("num_opinion"))\
        .join(JobCandidate)\
        .filter(JobCandidate.job_id == job_id, JobCandidateOpinion.opinion.in_(["like", "dislike"]))\
        .group_by(JobCandidateOpinion.opinion)\
        .all()

    # number of note per candidate
    candidate_notes = db.session.query(JobCandidate, func.count(JobCandidateNote.note).label("num_notes"))\
        .join(JobCandidateNote)\
        .filter(JobCandidate.job_id == job_id)\
        .group_by(JobCandidate.candidate_id)\
        .all()

    # number of matches
    candidate_matches = db.session.query(JobCandidate.candidate_id, JobCandidate.match_counter)\
        .filter(JobCandidate.job_id == job_id)\
        .all()

    # results
    result = {job_opinion.opinion: job_opinion.num_opinion for job_opinion in job_opinions}
    result["num_match_per_candidate"] = {candidate.candidate_id: candidate.match_counter for candidate in candidate_matches}
    result["num_notes_per_candidate"] = {candidate_note.JobCandidate.candidate_id: candidate_note.num_notes
                                         for candidate_note in candidate_notes}

    return {"results": {"status": "success", "stats": result}}, 200
