import enum
import re
from datetime import datetime, timezone

from flask_login import UserMixin
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


profile_waste_types = db.Table(
    "profile_waste_types",
    db.Column("profile_id", db.Integer, db.ForeignKey("profiles.id"), primary_key=True),
    db.Column("waste_type_id", db.Integer, db.ForeignKey("waste_types.id"), primary_key=True),
)


class TimestampMixin:
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    class Role(enum.StrEnum):
        COLLECTOR = "collector"
        AGENCY = "agency"
        ADMIN = "admin"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)

    profile = db.relationship(
        "Profile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class Profile(TimestampMixin, db.Model):
    __tablename__ = "profiles"

    class Status(enum.StrEnum):
        PENDING = "pending"
        APPROVED = "approved"
        SUSPENDED = "suspended"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    display_name = db.Column(db.String(150), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))
    status = db.Column(db.Enum(Status), nullable=False, default=Status.APPROVED, index=True)

    user = db.relationship("User", back_populates="profile")
    waste_types = db.relationship(
        "WasteType",
        secondary=profile_waste_types,
        lazy="joined",
        order_by="WasteType.name",
    )

    @property
    def location_label(self):
        return ", ".join(part for part in [self.area, self.city, self.region] if part)

    @property
    def waste_type_names(self):
        return ", ".join(waste.name for waste in self.waste_types)

    @property
    def public_role_label(self):
        mapping = {
            User.Role.COLLECTOR: "Collector",
            User.Role.AGENCY: "Recycling Agency",
            User.Role.ADMIN: "Admin",
        }
        return mapping.get(self.user.role, "Member")

    @property
    def whatsapp_url(self):
        digits = re.sub(r"\D", "", self.user.phone or "")
        if digits.startswith("0"):
            digits = f"233{digits[1:]}"
        elif digits.startswith("233"):
            digits = digits
        elif digits and not digits.startswith("+" ):
            digits = digits
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def image_url(self):
        if not self.image_filename:
            return None
        return f"uploads/{self.image_filename}"

    @property
    def image_src(self):
        if not self.image_filename:
            return None
        if self.image_filename.startswith(("https://", "http://")):
            return self.image_filename
        return url_for("static", filename=self.image_url)

    @property
    def initials(self):
        words = [word[0] for word in re.findall(r"[A-Za-z0-9]+", self.display_name or "")]
        if words:
            return "".join(words[:2]).upper()
        return (self.display_name or "EG")[:2].upper()

    @property
    def status_label(self):
        if self.status == self.Status.SUSPENDED:
            return "Suspended"
        return "Active"

    @property
    def is_public(self):
        return self.status != self.Status.SUSPENDED and self.user.role != User.Role.ADMIN


class WasteType(db.Model):
    __tablename__ = "waste_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class ContactSubmission(TimestampMixin, db.Model):
    __tablename__ = "contact_submissions"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    message = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
