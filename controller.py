from flask import Flask, request
from flask import jsonify

from tricount_anaylzer import TricountAnalyzer

methods = ('GET', 'POST')


class Controller:

    def __init__(self, port, analyzer: TricountAnalyzer):
        self.analyzer = analyzer
        self.app = Flask(__name__)
        self.init_route()
        self.app.run(port=port)

    def init_route(self):
        @self.app.route("/", methods=methods)
        def health():
            return "ok"

        @self.app.route("/search", methods=methods)
        def find_metrics():
            return jsonify(self.analyzer.get_metrics())

        @self.app.route("/query", methods=methods)
        def d():
            req = request.get_json()
            print(req)
            scoped_var = req["scopedVars"]
            target = req["targets"][0]["target"]
            res = self.analyzer.answer_query(target, scoped_var)
            return jsonify(res)

        @self.app.route("/tag-keys", methods=methods)
        def d2():
            res = [
                {
                    "type": "string", "text": "User"
                },
            ]
            return jsonify(res)

        @self.app.route("/tag-values", methods=methods)
        def d22():
            res = list()
            for user in self.analyzer.get_users():
                res.append({"text": user})
            return jsonify(res)

        @self.app.route("/variable", methods=methods)
        def d222():
            req = request.get_json()
            print(req)
            res = list()
            for user in self.analyzer.get_users():
                res.append({"__text": user, "__value": user})
            return jsonify(res)
