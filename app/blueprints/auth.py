from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms import LoginForm, ProfileForm, RegisterForm
from ..mailer import send_email
from ..models import Profile, User, WasteType
from ..utils import save_uploaded_image


auth_bp = Blueprint("auth", __name__)


def _waste_choices():
    return [(item.id, item.name) for item in WasteType.query.order_by(WasteType.name.asc()).all()]


@auth_bp.route("/register", methods=["GET", "POST"])
@auth_bp.route("/join", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.edit_profile"))

    form = RegisterForm()
    form.waste_types.choices = _waste_choices()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            form.email.errors.append("An account with that email already exists.")
        else:
            user = User(
                email=email,
                phone=form.phone.data.strip(),
                role=User.Role(form.role.data),
            )
            user.set_password(form.password.data)

            profile = Profile(
                display_name=form.display_name.data.strip(),
                region=form.region.data.strip(),
                city=form.city.data.strip(),
                area=form.area.data.strip(),
                description=form.description.data.strip(),
                status=Profile.Status.APPROVED,
            )
            if form.image.data:
                profile.image_filename = save_uploaded_image(form.image.data)

            profile.waste_types = WasteType.query.filter(WasteType.id.in_(form.waste_types.data)).all()
            user.profile = profile

            db.session.add(user)
            db.session.commit()

            login_user(user)
            confirmation_sent = send_email(
                recipients=email,
                subject="Your EcoBridge Ghana account is ready",
                body=(
                    f"Hello {profile.display_name},\n\n"
                    "Your EcoBridge Ghana account has been created successfully.\n"
                    "You can sign in and use your profile right away.\n\n"
                    f"Website: {url_for('main.home', _external=True)}\n"
                    f"Public contact: {current_app.config['CONTACT_RECIPIENT']}\n\n"
                    "Thank you for joining EcoBridge Ghana."
                ),
            )
            if confirmation_sent:
                flash(
                    f"Registration complete. Your account is active and a confirmation email has been sent to {email}.",
                    "success",
                )
            else:
                flash("Registration complete. Your account is active and ready to use.", "success")
            return redirect(url_for("auth.edit_profile"))

    return render_template(
        "auth/register.html",
        page_title="Join the Network",
        meta_description="Register as a waste collector or recycling agency on EcoBridge Ghana.",
        form=form,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back to EcoBridge Ghana.", "success")
            return redirect(url_for("main.home"))

        flash("Invalid email or password.", "danger")

    return render_template(
        "auth/login.html",
        page_title="Sign In",
        meta_description="Sign in to manage your EcoBridge Ghana listing.",
        form=form,
    )


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    form = ProfileForm(obj=profile)
    form.waste_types.choices = _waste_choices()

    if not current_user.is_admin:
        form.status.render_kw = {"disabled": True}

    if form.validate_on_submit():
        if form.email.data.strip().lower() != current_user.email:
            duplicate = User.query.filter_by(email=form.email.data.strip().lower()).first()
            if duplicate and duplicate.id != current_user.id:
                form.email.errors.append("Another account already uses that email.")
                return render_template(
                    "auth/profile_edit.html",
                    page_title="Edit Profile",
                    meta_description="Update your EcoBridge Ghana listing details.",
                    form=form,
                    profile=profile,
                )

        current_user.email = form.email.data.strip().lower()
        current_user.phone = form.phone.data.strip()
        profile.display_name = form.display_name.data.strip()
        profile.region = form.region.data.strip()
        profile.city = form.city.data.strip()
        profile.area = form.area.data.strip()
        profile.description = form.description.data.strip()
        profile.waste_types = WasteType.query.filter(WasteType.id.in_(form.waste_types.data)).all()

        if current_user.is_admin:
            profile.status = Profile.Status(form.status.data)

        if form.image.data:
            profile.image_filename = save_uploaded_image(form.image.data)

        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("auth.edit_profile"))

    if not form.is_submitted():
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.waste_types.data = [item.id for item in profile.waste_types]
        form.status.data = (
            profile.status.value
            if profile.status != Profile.Status.PENDING
            else Profile.Status.APPROVED.value
        )

    return render_template(
        "auth/profile_edit.html",
        page_title="Edit Profile",
        meta_description="Update your EcoBridge Ghana listing details.",
        form=form,
        profile=profile,
    )
