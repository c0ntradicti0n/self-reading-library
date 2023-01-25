import os
import subprocess
import logging
from pathlib import Path
import coloredlogs
from flask import g, Response, request
from flask_restx import Resource, Api
from flaskoidc import FlaskOIDC
from flaskoidc.config import BaseConfig
from dotenv import load_dotenv
import jwt
import time
import shlex


def escape(c):
    return c


load_dotenv()
coloredlogs.install(level="DEBUG")
BaseConfig.CONFIG_URL = (
    "http://keycloak:9080/realms/tbdk/.well-known/openid-configuration"
)
BaseConfig.PROVIDER_NAME = "keycloak"
BaseConfig.OIDC_CLIENT_ID = "frontend"

app = FlaskOIDC(os.getcwd() + __name__)
api = Api(app)
ns = api.namespace("forum", description="Api for FS forum")
user = api.namespace("user", description="Api for OS/Keycloak user")
d = "."

original_umask = os.umask(0)
os.makedirs(d, exist_ok=True, mode=0o777)


def __user__():
    info = g._oauth_token_keycloak
    user = jwt.decode(info["access_token"], options={"verify_signature": False})
    return [user.get("preferred_username"), user.get("sub")]


def o(cmd, user=None, dir="./", err_out=True):
    if not user:
        user = __user__()[0]
    try:
        logging.info(f"calling {user=}: " + cmd)
        # logging.info(user + str([shlex.quote(c) for c in shlex.split((cmd))]))

        output, error = subprocess.Popen(
            [shlex.quote(c) for c in shlex.split((cmd))],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=dir,
            user=user,
        ).communicate()
        if error and err_out:
            raise (Exception(error.decode()))
    except PermissionError:
        logging.error("can only run in docker")
    except Exception as e:
        logging.error(e, exc_info=True)
    return output.decode()


c = os.getcwd()


def swag_flask(converter):
    conv_ns = api.namespace(converter.__class__, description=converter.__doc__)

    @conv_ns.route("/" + converter.uri)
    class _:
        pass

    return _


insight = api.namespace("insight", description="Inspection API")


@app.before_request
def before():
    try:
        os.chdir(d)
        g.start = time.time()
    except:
        pass


@app.after_request
def after(response):
    try:
        os.chdir(c)
        diff = time.time() - g.start
        logging.info("time " + str(diff) + "s")
    except:
        pass

    return response


@api.errorhandler(FileNotFoundError)
@api.errorhandler(Exception)
def handle_no_result_exception(error):
    """Return a custom not found error message and 404 status code"""
    logging.error(error, exc_info=True)
    return {"message": str("".join(error.args))}, 404


@ns.route("/")
class forum(Resource):
    @ns.param("name", "forum path")
    def get(self):
        name = request.args.get("name", default=".")
        return Response(
            o(f"tree '{escape(name)}' --noreport -lufp"),
            200,
            {"content-type": "text/plain"},
        )

        return Response(o(f" ls  -Hla"), 200, {"content-type": "text/plain"})

    @ns.param("name", "forum path")
    def post(self):
        with log():
            name = request.args.get("name")
            return Response(o(f"mkdir -m 777 '{escape(name)}'"))

    @ns.param("source", "which forum to show elsewhere")
    @ns.param("target", "where to show")
    def patch(self):
        source = request.args.get("source", default=None, type=str)
        target = request.args.get("target", default=None, type=str)
        return Response(
            o(
                f"ln -s '../{escape(source)}' '{os.getcwd()}/{escape(target)}'",
                user="root",
            ),
            203,
            {"content-type": "text/plain"},
        )

    @ns.param("name", "forum path")
    def delete(self):
        name = request.args.get("name")
        return Response(
            o(f"rm -r '{escape(name)}'"), 204, {"content-type": "text/plain"}
        )


@ns.route("/threads")
class threads(Resource):
    def get(self):
        return Response(o("find . -type f"))


@ns.route("/thread")
@ns.param("name", "forum path")
class thread(Resource):
    def get(self):
        name = request.args.get("name")
        return Response(o(f"cat '{escape(name)}'"))

    @ns.doc(params={"content": "question", "name": "path of forum"})
    def post(self):
        user = __user__()[0]

        with log():
            name, content = request.args.get("name"), request.args.get("content")
            with open(name, "w", mode=0o777) as f:
                f.write(f"question:\n\tcontent: {content}\n\tuser: {user}\nresponse:")
            o(f"chown '{user}' '{name}' ", user="root")
        return Response(Path(name).read_text())


@ns.route("/post")
@api.doc(params={"name": "a thread path"})
class post(Resource):
    def get(self):
        name = request.args.get("name")
        return Response(o(f"tail -n +4 '{escape(name)}'"))

    @ns.doc(params={"content": "response"})
    def post(self):
        user = __user__()[0]

        with log():
            name, content = request.args.get("name"), request.args.get("content")
            if os.path.exists(name):
                o(f"chown '{user}' '{name}' ", user="root")
                with open(name, "a") as f:
                    f.write(
                        f"\n\t{time.strftime('%Y-%m-%d %H:%M')}: \n\t\tcontent: {content}\n\t\tuser: {user}"
                    )

            return Response(Path(name).read_text())


@user.route("/permissionis")
class Permissions(Resource):
    def get(self, name):
        return Response(o(f"ls {name} -la"))


@user.route("/create")
@ns.doc(params={"group": "group", "name": "user"})
class create(Resource):
    def get(self):
        name = request.args.get("name")
        group = request.args.get("group", default="user")
        add_user(group, name)
        return Response(True)


@user.route("/group")
class group(Resource):
    def get(self):
        return Response(o(f"id -g"))


@user.route("/groups")
class groups(Resource):
    def get(self):
        return Response(o(f"groups"))


@user.route("/logs")
class Logs(Resource):
    def get(self):
        return Response(o(f"git log"))


@user.route("/")
class User(Resource):
    def get(self):
        [username, user_id] = __user__()
        return Response(o("id -a") + str([username, user_id]))


for url, ops in app.url_map.__dict__["_rules_by_endpoint"].items():
    for op in ops:
        for method in op.methods:
            if method in ["HEAD", "OPTIONS"]:
                continue
            path = f"../.py/test/{op.rule}_{method}"
            if not os.path.exists(path):
                os.makedirs(os.path.split(os.path.abspath(path))[0], exist_ok=True)
                with open(path, "w") as f:
                    f.write(
                        f"""
{method} http://localhost:5000{op.rule}

""".replace(
                            "<path:filename>", "bla"
                        )
                    )

if __name__ == "__main__":
    app.run(
        debug=True if not os.environ.get("PROD", None) else False,
        host="0.0.0.0",
        threaded=True,
    )
