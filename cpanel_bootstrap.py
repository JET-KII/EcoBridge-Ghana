import os

from app import create_app
from app.extensions import db
from app.models import Profile, User, WasteType


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


def seed_admin():
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    admin_phone = os.getenv("ADMIN_PHONE", "").strip()

    if not admin_email or not admin_password:
        raise RuntimeError("Set ADMIN_EMAIL and ADMIN_PASSWORD before running this script.")

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


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_waste_types()
        seed_admin()
        print("Database initialized.")
        print(f"Admin ready: {os.getenv('ADMIN_EMAIL', '').strip().lower()}")


if __name__ == "__main__":
    main()
