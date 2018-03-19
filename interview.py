import json
import os, sys


from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

# Cross domain access.
cors = CORS(app)


@app.route('/')
def info():
    return 'This is the InterviewWebApp from Smartorg'


@app.route('/login', methods=['GET'])
def login1():
    return "hello hi"

@app.route('/login', methods=['POST'])
def login():
    #get all valid candidates email address
    def get_emailList():
        data = json.load(open('/opt/rangal//1.0.0/candidateInfo.json'))
        return data["validCandidateEmails"]

    valid_candidate_email_list = get_emailList()

    data = request.get_json()
    email = data['email']

    # if the user first time login
    if email in valid_candidate_email_list and not os.path.exists(
                    '%s.json' % email):
        os.makedirs('%s.json' % email)
        with open('%s.json' % email) as json_data:
            json_obj = json.load(json_data)
            json_obj['candidate'] = {
                "emailAddress": "e@e",
                "startTime": "",
                "isAnswerSubmitted": False,
                "submittedAnswer": {
                    "codes": ""
                },
                "submittedTime": ""
            }
            with open('%s.json' % email, 'w') as j:
                json.dump(json_obj, j)

    #if the user not first time log in and before deadline
    if os.path.exists('%s.json' % email):
        with open('%s.json' % email) as json_data:
            json_obj = json.load(json_data)
            # if current time - start time < 24 hours and submitted is false:
            #     with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #             return left time
            # if current time - start time > 24 hours and submitted is false:
            #     return "You run out of time, Sorry!"

    #if the user login after submitted
    if os.path.exists('%s.json' % email):
        with open('%s.json' % email) as json_data:
            json_obj = json.load(json_data)
            # if submitted is true and current time - start time < 24 hours:
            #   with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #             return left time and you can resubmit
            # if submitted is true and current time - start time >= 24 hours:
            #   with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #             return "you have submitted, relax!"


@app.route('/submit-answer/<email>/<answer>', methods=['POST'])
def submit_answer(email, answer):
    if os.path.exists('%s.json' % email):
        with open('%s.json' % email) as json_data:
            json_obj = json.load(json_data)
            # if submitted is false and current time - start time <= 24 hours:
            #     json_obj['candidate']['submittedAnswer'] = answer
            #     with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #         return left time and you can resubmit
            # if submitted is false and current time - start time > 24 hours:
            #     json_obj['candidate']['submittedAnswer'] = answer
            #     with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #         return run out of time, sorry
            # if submitted is true and current time - start time <= 24 hours:
            #     json_obj['candidate']['submittedAnswer'] = answer
            #     with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #         return left time and you can resubmit
            # if submitted is true and current time - start time >= 24 hours:
            #     json_obj['candidate']['submittedAnswer'] = answer
            #     with open('%s.json' % email, 'w') as j:
            #         json.dump(json_obj, j)
            #         return you have submitted, relax!

if __name__ == '__main__':
    app.run()
