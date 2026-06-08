from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..models import ContactSubmission, Profile, User
from ..utils import admin_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@login_required
@admin_required
def dashboard():
    total_members = User.query.filter(User.role != User.Role.ADMIN).count()
    active_profiles = (
        db.session.query(Profile)
        .join(User)
        .filter(Profile.status != Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)
        .count()
    )
    suspended_profiles = (
        db.session.query(Profile)
        .join(User)
        .filter(Profile.status == Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)
        .count()
    )
    recent_messages = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard",
        meta_description="Moderate EcoBridge Ghana listings and view contact submissions.",
        total_members=total_members,
        active_profiles=active_profiles,
        suspended_profiles=suspended_profiles,
        recent_messages=recent_messages,
    )


@admin_bp.get("/users")
@login_required
@admin_required
def users():
    members = (
        User.query.join(Profile)
        .filter(User.role != User.Role.ADMIN)
        .order_by(Profile.created_at.desc())
        .all()
    )
    return render_template(
        "admin/users.html",
        page_title="Manage Listings",
        meta_description="Review and moderate EcoBridge Ghana member listings.",
        members=members,
    )


@admin_bp.post("/users/<int:user_id>/activate")
@login_required
@admin_required
def activate_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.is_admin:
        flash("Admin accounts cannot be changed here.", "danger")
        return redirect(url_for("admin.users"))
    user.profile.status = Profile.Status.APPROVED
    db.session.commit()
    flash(f"{user.profile.display_name} is now active.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/role")
@login_required
@admin_required
def update_user_role(user_id):
    user = db.get_or_404(User, user_id)
    target_role = request.form.get("role", "").strip()
    allowed_roles = {
        User.Role.COLLECTOR.value: User.Role.COLLECTOR,
        User.Role.AGENCY.value: User.Role.AGENCY,
    }

    if user.is_admin:
        flash("Admin accounts cannot be switched here.", "danger")
        return redirect(url_for("admin.users"))

    if target_role not in allowed_roles:
        flash("Invalid role selected.", "danger")
        return redirect(url_for("admin.users"))

    if user.role == allowed_roles[target_role]:
        flash(f"{user.profile.display_name} is already set to {user.profile.public_role_label}.", "info")
        return redirect(url_for("admin.users"))

    user.role = allowed_roles[target_role]
    db.session.commit()
    flash(f"{user.profile.display_name} is now a {user.profile.public_role_label}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/suspend")
@login_required
@admin_required
def suspend_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.is_admin:
        flash("Admin accounts cannot be changed here.", "danger")
        return redirect(url_for("admin.users"))
    user.profile.status = Profile.Status.SUSPENDED
    db.session.commit()
    flash(f"{user.profile.display_name} has been suspended.", "warning")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/delete")
@login_required
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.is_admin:
        flash("Admin accounts cannot be deleted here.", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash("Listing removed.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.get("/messages")
@login_required
@admin_required
def messages():
    submissions = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).all()
    return render_template(
        "admin/messages.html",
        page_title="Contact Messages",
        meta_description="View contact submissions sent to EcoBridge Ghana.",
        submissions=submissions,
    )
