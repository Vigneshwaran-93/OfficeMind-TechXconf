import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

import config
from frontend import api_client

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("token"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/")
def index():
    return redirect(url_for("welcome") if session.get("token") else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        resp = api_client.post("/auth/register", json={
            "username": request.form["username"],
            "password": request.form["password"],
            "display_name": request.form.get("display_name") or None,
        })
        if resp.status_code == 200:
            session["token"] = resp.json()["access_token"]
            return redirect(url_for("welcome"))
        flash(resp.json().get("detail", "Registration failed"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        resp = api_client.post("/auth/login", json={
            "username": request.form["username"],
            "password": request.form["password"],
        })
        if resp.status_code == 200:
            session["token"] = resp.json()["access_token"]
            return redirect(url_for("welcome"))
        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html")


@app.route("/home")
@login_required
def home():
    resp = api_client.get("/questions")
    categories = resp.json()["categories"] if resp.status_code == 200 else {}
    return render_template("home.html", categories=categories)


@app.route("/questions/<category>")
@login_required
def questions(category):
    resp = api_client.get("/questions")
    data = resp.json() if resp.status_code == 200 else {"categories": {}, "checkin": {}}
    cat_data = data["categories"].get(category)
    if cat_data is None and category != "other":
        return redirect(url_for("home"))
    if category == "other":
        cat_data = {
            "title": "Something else",
            "stage1": [{"id": "something_else", "label": "Something else", "free_text": True}],
            "generic_stage2": [],
            "generic_stage3": [],
            "branches": {},
        }
    return render_template(
        "questions.html", category=category, cat_data=cat_data, checkin=data.get("checkin", {})
    )


@app.route("/session/start", methods=["POST"])
@login_required
def session_start():
    context = request.get_json()
    resp = api_client.post("/sessions/start", json={"context": context})
    if resp.status_code != 200:
        return jsonify({"error": resp.json().get("detail", "Could not start session")}), resp.status_code
    data = resp.json()
    session["session_id"] = data["session_id"]
    session["opening_message"] = data["opening_message"]
    session["category"] = context.get("category")
    session["preferred_interaction"] = context.get("preferred_interaction", "text")
    return jsonify({"redirect": url_for("companion")})


@app.route("/companion")
@login_required
def companion():
    if not session.get("session_id"):
        return redirect(url_for("home"))
    return render_template(
        "companion.html",
        session_id=session["session_id"],
        opening_message=session.get("opening_message", ""),
        preferred_interaction=session.get("preferred_interaction", "text"),
        max_audio_seconds=config.MAX_AUDIO_SECONDS,
    )


@app.route("/chat/text", methods=["POST"])
@login_required
def chat_text():
    body = request.get_json()
    resp = api_client.post("/chat/text", json={
        "session_id": session.get("session_id"),
        "message": body.get("message", ""),
    })
    return jsonify(resp.json()), resp.status_code


@app.route("/chat/voice", methods=["POST"])
@login_required
def chat_voice():
    audio_file = request.files.get("audio")
    files = {"audio": (audio_file.filename or "audio.webm", audio_file.stream, audio_file.mimetype)}
    data = {"session_id": str(session.get("session_id"))}
    resp = api_client.post("/chat/voice", data=data, files=files)
    return jsonify(resp.json()), resp.status_code


@app.route("/chat/tts", methods=["POST"])
@login_required
def chat_tts():
    body = request.get_json()
    resp = api_client.post("/chat/tts", json={"text": body.get("text", "")})
    return jsonify(resp.json()), resp.status_code


@app.route("/session/end", methods=["POST"])
@login_required
def session_end():
    body = request.get_json() or {}
    sid = session.get("session_id")
    resp = api_client.post(f"/sessions/{sid}/end", json={"feeling_after": body.get("feeling_after")})
    if resp.status_code != 200:
        return jsonify({"error": "Could not end session"}), resp.status_code
    session["plan"] = resp.json()
    session.pop("session_id", None)
    session.pop("opening_message", None)
    return jsonify({"redirect": url_for("plan")})


@app.route("/plan")
@login_required
def plan():
    plan_data = session.get("plan")
    if not plan_data:
        return redirect(url_for("home"))
    return render_template("plan.html", plan=plan_data)


@app.route("/plan/save", methods=["POST"])
@login_required
def plan_save():
    body = request.get_json()
    plan_data = session.get("plan") or {}
    resp = api_client.post("/sessions/plan/save", json={
        "session_id": plan_data.get("session_id"),
        "save": body.get("save", True),
    })
    return jsonify(resp.json()), resp.status_code


@app.route("/plan/feeling", methods=["POST"])
@login_required
def plan_feeling():
    body = request.get_json()
    plan_data = session.get("plan") or {}
    sid = plan_data.get("session_id")
    if sid:
        api_client.post(f"/sessions/{sid}/feeling", json={"feeling_after": body.get("feeling_after")})
    return jsonify({"ok": True})


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        kind = request.form.get("kind")
        value = request.form.get("value")
        if kind == "setting":
            value = f"{request.form.get('setting_key')}:{value}"
        if kind and value:
            api_client.post("/preferences", json={"kind": kind, "value": value})
        return redirect(url_for("profile"))

    resp = api_client.get("/preferences")
    prefs = resp.json() if resp.status_code == 200 else []
    grouped = {"like": [], "dislike": [], "trigger": [], "setting": [], "mask_term": []}
    for p in prefs:
        grouped.setdefault(p["kind"], []).append(p)
    return render_template("profile.html", grouped=grouped)


@app.route("/profile/delete/<int:pref_id>", methods=["POST"])
@login_required
def profile_delete(pref_id):
    api_client.delete(f"/preferences/{pref_id}")
    return redirect(url_for("profile"))


@app.route("/profile/delete-account", methods=["POST"])
@login_required
def delete_account():
    api_client.delete("/auth/me")
    session.clear()
    return redirect(url_for("login"))


@app.route("/help")
@login_required
def help_page():
    resp = api_client.get("/sessions/plans")
    saved_plans = resp.json() if resp.status_code == 200 else []
    return render_template("help.html", saved_plans=saved_plans)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=config.FRONTEND_PORT, debug=True)
