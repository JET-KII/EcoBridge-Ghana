import os
from pathlib import Path

from flask import Flask

from .config import get_config
from .content import SITE_SETTINGS
from .extensions import csrf, db, login_manager
from .models import ContactSubmission, Profile, User, WasteType


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_object))

    upload_path = Path(app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)

    register_extensions(app)
    register_blueprints(app)
    register_context_processors(app)
    register_cli_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    from .blueprints.admin import admin_bp
    from .blueprints.auth import auth_bp
    from .blueprints.directory import directory_bp
    from .blueprints.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(directory_bp)
    app.register_blueprint(admin_bp)


def register_context_processors(app):
    @app.context_processor
    def inject_site_meta():
        return {
            "site_name": SITE_SETTINGS["site_name"],
            "site_tagline": SITE_SETTINGS["site_mission"],
            "site_marketing_tagline": SITE_SETTINGS["site_marketing_tagline"],
            "site_subtitle": SITE_SETTINGS["site_subtitle"],
            "site_domain": SITE_SETTINGS["site_domain"],
            "site_url": SITE_SETTINGS["site_url"],
            "site_public_email": SITE_SETTINGS["site_public_email"],
            "site_phone_display": SITE_SETTINGS["site_phone_display"],
            "site_phone_href": SITE_SETTINGS["site_phone_href"],
            "site_social_handle": SITE_SETTINGS["site_social_handle"],
            "site_social_handle_raw": SITE_SETTINGS["site_social_handle_raw"],
            "site_instagram_url": SITE_SETTINGS["site_instagram_url"],
            "site_hashtag": SITE_SETTINGS["site_hashtag"],
            "site_footer_support_line": SITE_SETTINGS["site_footer_support_line"],
            "site_copyright": SITE_SETTINGS["site_copyright"],
        }


def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Create all database tables and seed baseline waste types."""
        db.create_all()
        seed_waste_types()
        print("Database initialized.")

    @app.cli.command("seed-admin")
    def seed_admin_command():
        """Create or update an administrator account from environment values."""
        db.create_all()
        seed_waste_types()

        admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "")
        admin_phone = os.getenv("ADMIN_PHONE", "").strip()

        if not admin_email or not admin_password:
            raise RuntimeError("Set ADMIN_EMAIL and ADMIN_PASSWORD before running seed-admin.")

        admin = User.query.filter_by(email=admin_email).first()
        if admin is None:
            admin = User(
                email=admin_email,
                phone=admin_phone,
                role=User.Role.ADMIN,
            )
            db.session.add(admin)
            db.session.flush()
        else:
            admin.role = User.Role.ADMIN
            admin.phone = admin_phone

        admin.set_password(admin_password)

        if admin.profile is None:
            admin.profile = Profile(
                display_name="EcoBridge Admin",
                region="Greater Accra",
                city="Accra",
                area="Airport",
                description="Administrative account for EcoBridge Ghana.",
                status=Profile.Status.APPROVED,
            )
        else:
            admin.profile.status = Profile.Status.APPROVED

        db.session.commit()
        print(f"Admin ready: {admin_email}")

    def seed_waste_types():
        default_types = [
            "Plastic",
            "Paper",
            "Metal",
            "Glass",
            "Organic",
            "Electronic Waste",
            "Textiles",
        ]
        existing = {item.name for item in WasteType.query.all()}
        for waste_name in default_types:
            if waste_name not in existing:
                db.session.add(WasteType(name=waste_name))
        db.session.commit()
