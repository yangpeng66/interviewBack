import json
import os, time, unicodedata, sys
from datetime import datetime, timedelta

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

# Cross domain access.
cors = CORS(app)

MAX_SUBMIT_TIMES = 5


def user_first_login(email):
    return not get_user_answer(email)


def init_user_answer(email):
    file_name = '%s.json' % email
    folder_path = '/opt/rangal/1.0.0/candidateAnswers'
    full_path = "{0}/{1}".format(folder_path, file_name)
    start_time = datetime.now()
    twentyfour_hours_from_start_time = start_time + timedelta(hours=24)
    data = {
        "emailAddress": email,
        "startTime": str(start_time),
        "deadLine": str(twentyfour_hours_from_start_time)[:19],
        "isAnswerSubmitted": False,
        "submittedAnswer": []
    }
    with open(full_path, 'w') as outfile:
        json.dump(data, outfile)
    return data


def get_user_answer(email):
    file_name = '%s.json' % email
    folder_path = '/opt/rangal/1.0.0/candidateAnswers'
    full_path = "{0}/{1}".format(folder_path, file_name)
    if os.path.exists(full_path):
        with open(full_path) as json_data:
            return json.load(json_data)
    else:
        return None


def save_user_answer(email, answer):
    file_name = '%s.json' % email
    folder_path = '/opt/rangal/1.0.0/candidateAnswers'
    full_path = "{0}/{1}".format(folder_path, file_name)
    with open(full_path, 'w') as outfile:
        json.dump(answer, outfile)


def get_emailList():
    data = json.load(open('/opt/rangal/1.0.0/candidateInfo.json'))
    return data["validCandidateEmails"]


def user_is_valid(email):
    valid_candidate_email_list = get_emailList()
    return email in valid_candidate_email_list


def user_is_not_expired(email):
    current_time = datetime.now()
    answer = get_user_answer(email)
    if answer is not None:
        dead_line = datetime.strptime(answer['deadLine'],
                                      "%Y-%m-%d %H:%M:%S")
        return current_time < dead_line
    else:
        return True


def can_user_submit(email):
    user_data = get_user_answer(email)
    return len(user_data['submittedAnswer']) < MAX_SUBMIT_TIMES


@app.route('/')
def info():
    return 'This is the InterviewWebApp from Smartorg'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email'].lower()

    # if the user first time login
    if user_is_valid(email) and user_first_login(email):
        user_data = init_user_answer(email)
        return json.dumps(
            {'canProceed': True, 'deadLine': user_data['deadLine']})

    # if the user not first time log in
    if user_is_valid(email):
        user_not_expired = user_is_not_expired(email)
        user_can_submit = can_user_submit(email)
        user_data = get_user_answer(email)
        if user_not_expired and user_can_submit:
            return json.dumps(
                {'canProceed': True, 'deadLine': user_data['deadLine']})
        elif not user_not_expired:
            return json.dumps(
                {'canProceed': False, 'message': 'Expired, sorry.'})
        elif not user_can_submit:
            return json.dumps(
                {'canProceed': False, 'message': 'You have reached the limit!'})
    else:
        return json.dumps({'canProceed': False,
                           'message': 'Your email has not in the ststem, please contack Melinda Gurman through email:mgurman@smartorg.com'})


@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    email = data['email'].lower()
    answer = data['answer']

    if user_is_valid(email) and user_is_not_expired(email) and can_user_submit(
            email):
        current_answer = get_user_answer(email)
        current_answer['submittedAnswer'].append({
            "codes": str(answer),
            "submittedTime": str(datetime.now())[:19]
        })
        save_user_answer(email, current_answer)
        return json.dumps({'success': 'You have submitted your answer!'})
    else:
        return json.dumps({'error': 'Not valid to submit, sorry.'})


@app.route('/get-challenge', methods=['POST'])
def get_challenge():
    # user valid, not expire, can submit
    data = request.get_json()
    email = data['email'].lower()

    if user_is_valid(email) and user_is_not_expired(email) and can_user_submit(
            email):
        current_answer = get_user_answer(email)
        submit_history = []
        if len(current_answer['submittedAnswer']) > 0:
            for a in current_answer['submittedAnswer']:
                submit_history.append(a['submittedTime'])

        return json.dumps({'question': """Find yourself in love with programming but haven't demonstrated it yet? No worries. Demonstrate your abilities by trying this challenge project in a language of your choice (we recommend Javascript). Write a program to unscramble anagrams (between 5 and 7 letters) and find the correct English word. (e.g. "leppa" would resolve to "apple", "ythitr" would resolve to "thirty", "gshinra" would resolve to "sharing")""",
                           'deadLine': current_answer['deadLine'], 'submitHistory': submit_history})
    else:
        return json.dumps({'error': 'Not valid for challenge question.'})


if __name__ == '__main__':
    app.run()
