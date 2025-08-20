from flask import Flask, jsonify, request

from flask_socketio import SocketIO

from flask_cors import CORS

from dotenv import load_dotenv

import os

import logging

import asyncio
 
from events import register_socket_events

from test_generator import generate_questions, TestRequest  # your async generator
 
# ✅ Supabase client

from supabase import create_client
 
load_dotenv()
 
SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
 
app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "defaultsecret")
 
# Disable Flask logs

log = logging.getLogger('werkzeug')

log.setLevel(logging.ERROR)
 
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

register_socket_events(socketio)
 
 
@app.route("/")

def index():

    return jsonify({"status": "Server is running."})
 
 
# GET test by ID (generate questions on the fly for demo)

@app.route("/api/test/<test_id>", methods=["GET"])

def get_test(test_id):

    try:

        test_request = TestRequest(

            topic=f"Demo topic for test {test_id}",

            difficulty="easy",

            num_questions=5,

            question_type="mcq",

            jd_id=test_id

        )
 
        questions = asyncio.run(generate_questions(test_request))

        return jsonify({"test_id": test_id, "questions": questions})
 
    except Exception as e:

        return jsonify({"error": str(e)}), 500
 
 
# POST generate test

@app.route("/api/test/generate", methods=["POST"])

def generate_test_route():

    try:

        data = request.get_json()

        test_request = TestRequest(

            topic=data.get("topic"),

            difficulty=data.get("difficulty", "easy"),

            num_questions=data.get("num_questions", 5),

            question_type=data.get("question_type", "mcq"),

            jd_id=data.get("jd_id"),

            mcq_count=data.get("mcq_count"),

            coding_count=data.get("coding_count")

        )

        questions = asyncio.run(generate_questions(test_request))

        return jsonify({"questions": questions})
 
    except Exception as e:

        return jsonify({"error": str(e)}), 500
 
 
# POST submit test

@app.route("/api/test/submit", methods=["POST"])

def submit_test():

    try:

        data = request.get_json()

        # TODO: Save answers if required

        return jsonify({"status": "success", "submitted_data": data})

    except Exception as e:

        return jsonify({"error": str(e)}), 500
 
 
# ✅ NEW: Get violation counts for a candidate & exam

@app.route("/api/violations/<candidate_id>/<exam_id>", methods=["GET"])

def get_violations(candidate_id, exam_id):

    try:

        response = supabase.table("violations").select("*").eq("candidate_id", candidate_id).eq("exam_id", exam_id).execute()

        violations = response.data
 
        # Count occurrences by type

        counts = {}

        for v in violations:

            vtype = v.get("violation_type")

            counts[vtype] = counts.get(vtype, 0) + 1
 
        return jsonify({"candidate_id": candidate_id, "exam_id": exam_id, "violations": counts})
 
    except Exception as e:

        return jsonify({"error": str(e)}), 500
 
 
if __name__ == "__main__":

    socketio.run(

        app,

        host="0.0.0.0",

        port=5000,

        debug=False,

        allow_unsafe_werkzeug=True  # Added for Render deployment

    )

 
