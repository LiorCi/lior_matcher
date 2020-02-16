
Overview
=======
A basic Flask web server which implements a “matcher” application and
some APIs for expressing opinions on that matcher. 
The application have 3 main models: Skill, Candidate, Job.
The application’s core function is “CandidateFinder” which given a job, returns the best
candidates for this job according to the following algorithm:
 1. candidate with match title* and skill
 2. candidate with match title will be first,
 3. candidate with no title match only skill match
 
*match title- at least one of the words in a job title match to at least one word in a candidate title

Prerequisites
==========
1. python version 3.6+
2. mysql server

Installing
==========
github:
```bash
git clone https://github.com/LiorCi/lior_matcher.git
```
install requirments on your venv: 
```bash
pip install -r requirments.txt
```
change db configuration on config.py
# run project
```python app.py```

Usage
=====

# flask admin
You can create skills, candidates and jobs using flask admin on: http://127.0.0.1:5000/ \
*first create skills \
**after creating candidates in the candidate tab, add their skiils in the candidate skill tab

### examples
2.5. Get matching candidates for a job. (only open jobs, whiteout opinion on the job candidate match)
```http://127.0.0.1:5000/jobs/<job_id>/candidates/match``` [GET]
```json
{
    "results": {
        "matches": [
            {
                "candidate_id": 3,
                "candidate_title": "software engineer"
            },
            {
                "candidate_id": 2,
                "candidate_title": "developer"
            },
            {
                "candidate_id": 4,
                "candidate_title": "human resources professional"
            }
        ],
        "status": "success"
    }
}
```
2.6. Add opinion on a matching candidate regarding a specific job, only on a open job
```http://127.0.0.1:5000/jobs/<job_id>/candidates/<candidate_id>/opinions``` [POST] \
```params: {"opinion": <opinion>}``` #optional param, default is 'like'

2.7. Get the liked candidates for a specific job (sorted by time of “like”). If the job is closed, return 0 candidates.
```http://127.0.0.1:5000/jobs/<job_id>/candidates/likes ``` [GET]
```json
{
    "results": {
        "candidates": {
            "1": {
                "candidate_id": 1,
                "note": [
                    "this is a note",
                    "candidate 1 is good",
                ],
                "title": "software developer"
            }
        },
        "status": "success"
    }
}
```

2.8. Add notes on liked candidate regarding a specific job, only on a liked candidate 
```http://127.0.0.1:5000/jobs/1/candidates/<candidate_id>/notes``` [POST] \
```params: {"note": <note>}``` required

2.9. get statistics on a job \
    1. Number of likes \
    2. Number of dislikes \
    3. Number of notes per candidate \
    4. Number of times a candidate was returned as ״matched״ for a job

```http://127.0.0.1:5000/jobs/<job_id>/statistics ``` [GET]
```json
{
    "results": {
        "stats": {
            "like": 4,
            "num_match_per_candidate": {
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 2
            },
            "num_notes_per_candidate": {
                "1": 10,
                "2": 1
            }
        },
        "status": "success"
    }
}
```
