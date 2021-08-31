import os

from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_grants")
def get_grants():
    grants = list(mongo.db.grants.find())
    return render_template("grants.html", grants=grants)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if the Username already exists in the DB
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "organisation": request.form.get("organisation").lower(),
            "website": request.form.get("website").lower()
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("You have been successfully registered as a new user!")
        flash("You may now view the full list of Grants within our Database,")
        flash("or add details of a new grant to share with other users.")
        return redirect(url_for("my_account", username=session["user"]))

    # Dynamically generate organisation options
    organisations = mongo.db.organisations.find().sort("organisation_name", 1)
    return render_template("register.html", organisations=organisations)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if Username exists in DB
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check password matches user input
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get(
                    "username", "first_name").lower()
                # added first_name above but may need to remove again
                # session["user"] = request.form.get("firstName")
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "my_account", username=session["user"]))
                # flash("Welcome, {}", mongo.db.user.find_one("firstName"))
                # flash("Welcome, {}".format.mongo.db.user.find_one(
                # "firstName"))
            else:
                # Invalid Password
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # Username doesn't match
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/my_account/<username>", methods=["GET", "POST"])
def my_account(username):
    # Get session user's username from the DB
    username = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if session["user"]:
        return render_template("my_account.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies and logout
    flash("You have been logged out!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_grant", methods=["GET", "POST"])
def add_grant():
    if request.method == "POST":
        is_recurring = "Yes" if request.form.get("is_recurring") else "No"
        grant = {
            "grant_title": request.form.get("grant_title"),
            "issuing_body": request.form.get("issuing_body"),
            "category_name": request.form.get("category_name"),
            "opening_date": request.form.get("opening_date"),
            "closing_date": request.form.get("closing_date"),
            "grant_description": request.form.get("grant_description"),
            "website": request.form.get("website"),
            "support_docs": request.form.get("support_docs"),
            "application_link": request.form.get("application_link"),
            "is_recurring": is_recurring,
            "created_by": session["user"]
        }
        mongo.db.grants.insert_one(grant)
        flash("Grant Details Successfully Added")
        return redirect(url_for("get_grants"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_grant.html", categories=categories)


@app.route("/edit_grant/<grant_id>", methods=["GET", "POST"])
def edit_grant(grant_id):
    if request.method == "POST":
        is_recurring = "Yes" if request.form.get("is_recurring") else "No"
        submit = {
            "grant_title": request.form.get("grant_title"),
            "issuing_body": request.form.get("issuing_body"),
            "category_name": request.form.get("category_name"),
            "opening_date": request.form.get("opening_date"),
            "closing_date": request.form.get("closing_date"),
            "grant_description": request.form.get("grant_description"),
            "website": request.form.get("website"),
            "support_docs": request.form.get("support_docs"),
            "application_link": request.form.get("application_link"),
            "is_recurring": is_recurring,
            "created_by": session["user"]
        }
        mongo.db.grants.update({"_id": ObjectId(grant_id)}, submit)
        flash("Grant Details Successfully Updated")

    grant = mongo.db.grants.find_one({"_id": ObjectId(grant_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_grant.html", grant=grant,
            categories=categories)


@app.route("/delete_grant/<grant_id>")
def delete_grant():
    mongo.db.grant.remove({"_id": ObjectId(grant_id)})
    flash("Grant Details Successfully Deleted")
    return redirect(url_for("get_grants"))


@app.route("/get_maintenance")
def get_maintenance():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    users = list(mongo.db.users.find().sort("username", 1))
    organisations = list(mongo.db.organisations.find().sort(
        "organisation_name", 1))
    return render_template("maintenance.html", categories=categories,
        users=users, organisations=organisations)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Successfully Added")
        return redirect(url_for("get_maintenance"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Succesfully Updated")
        return redirect(url_for("get_maintenance"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_maintenance"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
