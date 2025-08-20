from flask_socketio import SocketIO

from supabase import create_client

import os
 
SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
 
def register_socket_events(socketio: SocketIO):

    @socketio.on("connect")

    def handle_connect():

        pass  # Keep silent
 
    @socketio.on("disconnect")

    def handle_disconnect():

        pass  # Keep silent
 
    @socketio.on("suspicious_event")

    def handle_suspicious_event(data):

        candidate_id = data.get("candidate_id")

        exam_id = data.get("exam_id")

        violation_type = data.get("violation_type")

        timestamp = data.get("timestamp")
 
        if not candidate_id or not exam_id or not violation_type:

            return  # Ignore incomplete data
 
        # ✅ 1. Insert raw violation log

        supabase.table("violations").insert({

            "candidate_id": candidate_id,

            "exam_id": exam_id,

            "violation_type": violation_type,

            "timestamp": timestamp

        }).execute()
 
        # ✅ 2. Map violation → summary column

        column_map = {

            "tab_switch": "tab_switches",

            "inactivity": "inactivities",

            "text_selection": "text_selections",

            "copy": "copies",

            "paste": "pastes",

            "right_click": "right_clicks"

        }
 
        if violation_type in column_map:

            col = column_map[violation_type]
 
            # Call Postgres function to increment

            try:

                supabase.rpc("increment_feedback", {

                    "cand_id": candidate_id,

                    "exam": exam_id,

                    "field": col

                }).execute()

            except Exception as e:

                print(f"⚠️ Failed to update feedback summary: {e}")

 
