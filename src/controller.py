import logging

from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth
from src.apli_client import ApiClient
from src.sql_client import SqlClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

methods = ('GET', 'POST')


class Controller:

    def __init__(self, port, api_client: ApiClient, sql_client: SqlClient, tricount_nb_threshold: int,
                 user_password: str, admin_password: str, refresh_rate: int):
        self.api_client = api_client
        self.sql_client = sql_client
        self.refresh_rate = refresh_rate
        self.tricount_nb_threshold = tricount_nb_threshold
        self.app = Flask(__name__)
        self.users = {
            "user": generate_password_hash(user_password),
            "admin": generate_password_hash(admin_password)
        }
        limiter = Limiter(
            self.app,
            key_func=get_remote_address,
            default_limits=["30 per minute", "1000 per hour"]
        )
        self.auth = HTTPBasicAuth()
        self.init_route()
        self.app.run(port=port, host="0.0.0.0")

    def init_route(self):
        @self.auth.verify_password
        def verify_password(username, password):
            if username in self.users and \
                    check_password_hash(self.users.get(username), password):
                return username

        @self.app.route("/", methods=["GET"])
        @self.auth.login_required
        def index():
            tricounts = self.sql_client.get_existing_tricounts()
            return render_template('index.html', tricounts=tricounts, refresh_rate=self.refresh_rate)

        @self.app.route("/add_tricount", methods=["POST"])
        @self.auth.login_required
        def add_tricount():
            new_tricount_id = request.form.get("tricount_id")
            if new_tricount_id is None:
                return "Missing tricount_id param", 400
            existing_tricount = self.sql_client.get_existing_tricounts()
            if len(existing_tricount) >= self.tricount_nb_threshold:
                return "Tricount threshold reached", 400
            for tr in existing_tricount:
                if tr.tr_id == new_tricount_id:
                    return "Tricount already imported", 409
            try:
                new_tr = self.api_client.get_tricount_model(new_tricount_id)
            except Exception as e:
                return "Tricount id invalid (or tricount API down)", 404
            self.sql_client.sync_tricount(new_tr)
            logging.info(f"Added new tricount {new_tr.title}, {new_tr.tr_id}")
            return "K bro", 200

        @self.app.route("/remove_tricount", methods=["POST"])
        @self.auth.login_required
        def remove_tricount():
            if self.auth.current_user() != "admin":
                return "Insufficient permissions", 403
            _tricount_id \
                = request.form.get("tricount_id")
            if _tricount_id is None:
                return "Missing tricount_id param", 400
            existing_tricounts = self.sql_client.get_existing_tricounts()
            for tr in existing_tricounts:
                if tr.tr_id == _tricount_id:
                    self.sql_client.delete_tricount(tr.uuid)
                    logging.info(f"Removed tricount {tr.title}, {tr.tr_id}")
                    return "K bro", 200
            return "Tricount not imported", 409