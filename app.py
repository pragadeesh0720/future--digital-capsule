from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from datetime import datetime

from database import create_table

from capsule import (
    create_capsule,
    get_capsule,
    get_all_capsules,
    delete_capsule,
    open_capsule,
    is_unlocked,
    get_remaining_time,
    is_password_locked
)


app = Flask(__name__)

app.secret_key = "change-this-secret-key"

create_table()


@app.route("/")
def home():

    capsules = get_all_capsules()

    return render_template(
        "index.html",
        capsules=capsules
    )


@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        title = request.form["title"].strip()

        message = request.form["message"].strip()

        unlock_time = request.form["unlock_time"]

        password = request.form["password"]

        confirm_password = request.form[
            "confirm_password"
        ]


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("create")
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("create")
            )


        capsule_id = create_capsule(
            title,
            message,
            unlock_time,
            password
        )


        return redirect(
            url_for(
                "view_capsule",
                capsule_id=capsule_id
            )
        )


    return render_template("create.html")


@app.route("/capsule/<int:capsule_id>", methods=["GET", "POST"])
def view_capsule(capsule_id):

    capsule = get_capsule(capsule_id)

    if capsule is None:

        return render_template(
            "error.html",
            message="Capsule not found."
        )


    unlocked = is_unlocked(
        capsule["unlock_time"]
    )

    message = None
    error = None


    if request.method == "POST":

        password = request.form["password"]

        message, error = open_capsule(
            capsule_id,
            password
        )

        capsule = get_capsule(capsule_id)


    return render_template(
        "view.html",
        capsule=capsule,
        unlocked=unlocked,
        message=message,
        error=error,
        remaining=get_remaining_time(
            capsule["unlock_time"]
        ),
        password_locked=is_password_locked(
            capsule
        )
    )


@app.route(
    "/capsule/<int:capsule_id>/delete",
    methods=["POST"]
)
def delete(capsule_id):

    delete_capsule(capsule_id)

    flash(
        "Capsule deleted.",
        "success"
    )

    return redirect(
        url_for("home")
    )

@app.context_processor
def inject_now():

    return {
        "now_string":
            datetime.now().strftime(
                "%Y-%m-%dT%H:%M"
            )
    }


if __name__ == "__main__":

    app.run(
        debug=True
    )