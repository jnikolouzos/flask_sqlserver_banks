# app.py
"""
Flask CRUD application using SQL Server as the database.
Manages a single data model: Bank (id, name, location).

This file contains:
- Application factory (create_app)
- SQLAlchemy model for Bank
- HTML routes with forms for basic UI
- RESTful API routes for programmatic access
"""

import os
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy object without app (to allow factory pattern)
db = SQLAlchemy()


class Bank(db.Model):
    """
    Bank model representing a bank entity in the database.

    Columns:
    - id: Primary key
    - name: Bank name
    - location: Bank location (e.g., city or country)
    """

    __tablename__ = "Banks"  # Match the table name created in db_init.sql

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Helper method to serialize Bank object to a dictionary."""
        return {"id": self.id, "name": self.name, "location": self.location}


def create_app(test_config=None):
    """
    Application factory to create and configure the Flask app.

    Using a factory pattern makes testing easier because we can
    create an app with a different configuration (e.g., SQLite).
    """
    app = Flask(__name__)

    # Secret key for secure sessions and flash messages
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Default SQL Server connection string.
    # You SHOULD override this via the DATABASE_URL environment variable in real usage.
    # Example:
    #   export DATABASE_URL="mssql+pyodbc://username:password@localhost:1433/BankDB?driver=ODBC+Driver+17+for+SQL+Server"
    default_db_url = (
        "mssql+pyodbc://username:password@localhost:1433/BankDB"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # For tests, we can pass a different configuration (e.g. SQLite)
    if test_config:
        app.config.update(test_config)

    # Initialize SQLAlchemy with this app
    db.init_app(app)

    # Create tables if they do not exist (in a real system you'd run migrations instead)
    with app.app_context():
        db.create_all()

    # -------------- HTML ROUTES (for browser / forms) -----------------

    @app.route("/")
    def index():
        """Home page: redirect to the list of banks."""
        return redirect(url_for("list_banks"))

    @app.route("/banks")
    def list_banks():
        """
        Display a list of all banks in the database.

        This is the "Read All" part of CRUD for the web UI.
        """
        banks = Bank.query.all()
        return render_template("banks_list.html", banks=banks)

    @app.route("/banks/<int:bank_id>")
    def bank_detail(bank_id):
        """
        Display details for a specific bank.

        Shows bank name and location ("Read One" in CRUD).
        """
        bank = Bank.query.get_or_404(bank_id)
        return render_template("bank_detail.html", bank=bank)

    @app.route("/banks/new", methods=["GET", "POST"])
    def create_bank():
        """
        Render a form to create a new bank (GET),
        and handle form submission (POST).

        This is the "Create" part of CRUD for the web UI.
        """
        if request.method == "POST":
            name = request.form.get("name")
            location = request.form.get("location")

            # Basic validation: ensure both fields are filled
            if not name or not location:
                flash("Name and location are required.", "error")
                return redirect(url_for("create_bank"))

            # Create and save new Bank instance
            new_bank = Bank(name=name, location=location)
            db.session.add(new_bank)
            db.session.commit()

            flash("Bank created successfully!", "success")
            return redirect(url_for("list_banks"))

        # If GET request, render the empty form template
        return render_template("bank_form.html")

    @app.route("/banks/<int:bank_id>/edit", methods=["GET", "POST"])
    def edit_bank(bank_id):
        """
        Render a form to edit an existing bank (GET),
        and handle the update (POST).

        This is the "Update" part of CRUD for the web UI.
        """
        bank = Bank.query.get_or_404(bank_id)

        if request.method == "POST":
            name = request.form.get("name")
            location = request.form.get("location")

            if not name or not location:
                flash("Name and location are required.", "error")
                return redirect(url_for("edit_bank", bank_id=bank.id))

            bank.name = name
            bank.location = location
            db.session.commit()

            flash("Bank updated successfully!", "success")
            return redirect(url_for("bank_detail", bank_id=bank.id))

        # If GET request, render the form with existing values
        return render_template("bank_edit.html", bank=bank)

    @app.route("/banks/<int:bank_id>/delete", methods=["POST"])
    def delete_bank(bank_id):
        """
        Delete a bank from the database.

        This is the "Delete" part of CRUD for the web UI.
        """
        bank = Bank.query.get_or_404(bank_id)
        db.session.delete(bank)
        db.session.commit()

        flash("Bank deleted successfully!", "success")
        return redirect(url_for("list_banks"))

    # -------------- RESTful API ROUTES (JSON) -----------------

    @app.route("/api/banks", methods=["GET"])
    def api_get_banks():
        """
        API endpoint: Get all banks.

        Method: GET /api/banks
        Returns JSON list of banks.
        """
        banks = Bank.query.all()
        return jsonify([b.to_dict() for b in banks]), 200

    @app.route("/api/banks/<int:bank_id>", methods=["GET"])
    def api_get_bank(bank_id):
        """
        API endpoint: Get a single bank by ID.

        Method: GET /api/banks/<bank_id>
        Returns JSON representation of the bank.
        """
        bank = Bank.query.get_or_404(bank_id)
        return jsonify(bank.to_dict()), 200

    @app.route("/api/banks", methods=["POST"])
    def api_create_bank():
        """
        API endpoint: Create a new bank.

        Method: POST /api/banks
        Body: JSON { "name": "...", "location": "..." }
        """
        data = request.get_json() or {}
        name = data.get("name")
        location = data.get("location")

        if not name or not location:
            return (
                jsonify({"error": "Both 'name' and 'location' are required."}),
                400,
            )

        new_bank = Bank(name=name, location=location)
        db.session.add(new_bank)
        db.session.commit()

        return jsonify(new_bank.to_dict()), 201

    @app.route("/api/banks/<int:bank_id>", methods=["PUT", "PATCH"])
    def api_update_bank(bank_id):
        """
        API endpoint: Update an existing bank.

        Method: PUT or PATCH /api/banks/<bank_id>
        Body: JSON { "name": "...", "location": "..." }
        """
        bank = Bank.query.get_or_404(bank_id)
        data = request.get_json() or {}

        # Allow partial updates (PATCH-like behavior)
        if "name" in data:
            bank.name = data["name"]
        if "location" in data:
            bank.location = data["location"]

        db.session.commit()
        return jsonify(bank.to_dict()), 200

    @app.route("/api/banks/<int:bank_id>", methods=["DELETE"])
    def api_delete_bank(bank_id):
        """
        API endpoint: Delete a bank.

        Method: DELETE /api/banks/<bank_id>
        """
        bank = Bank.query.get_or_404(bank_id)
        db.session.delete(bank)
        db.session.commit()
        return jsonify({"message": "Bank deleted"}), 200

    return app


# If this file is executed directly, create an app and run the dev server.
if __name__ == "__main__":
    app = create_app()
    # debug=True enables hot reload during development (disable in production)
    app.run(debug=True)
