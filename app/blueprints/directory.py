from flask import Blueprint, abort, render_template, request
from flask_login import current_user
from sqlalchemy import or_

from ..extensions import db
from ..forms import SearchForm
from ..models import Profile, User, WasteType


directory_bp = Blueprint("directory", __name__, url_prefix="/directory")


@directory_bp.get("/")
def search():
    form = SearchForm(request.args)
    form.waste_type.choices = [("", "All waste types")] + [
        (str(item.id), item.name) for item in WasteType.query.order_by(WasteType.name.asc()).all()
    ]

    query = Profile.query.join(User).filter(Profile.status != Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)

    location = (request.args.get("location") or "").strip()
    user_type = (request.args.get("user_type") or "").strip()
    waste_type_id = (request.args.get("waste_type") or "").strip()

    if location:
        like_value = f"%{location}%"
        query = query.filter(
            or_(
                Profile.region.ilike(like_value),
                Profile.city.ilike(like_value),
                Profile.area.ilike(like_value),
            )
        )

    valid_roles = {User.Role.COLLECTOR.value, User.Role.AGENCY.value}
    if user_type in valid_roles:
        query = query.filter(User.role == User.Role(user_type))

    if waste_type_id.isdigit():
        query = query.join(Profile.waste_types).filter(WasteType.id == int(waste_type_id))

    profiles = query.order_by(Profile.created_at.desc()).all()

    return render_template(
        "directory/search.html",
        page_title="Search Collectors and Agencies",
        meta_description="Browse collectors and recycling agencies across Ghana by location and waste type.",
        form=form,
        profiles=profiles,
    )


@directory_bp.get("/<int:profile_id>")
def detail(profile_id):
    profile = db.get_or_404(Profile, profile_id)
    can_preview_private = current_user.is_authenticated and (
        current_user.is_admin or current_user.id == profile.user_id
    )

    if not profile.is_public and not can_preview_private:
        abort(404)

    return render_template(
        "directory/profile_detail.html",
        page_title=f"{profile.display_name} | EcoBridge Ghana",
        meta_description=f"Connect with {profile.display_name} through EcoBridge Ghana's recycling network.",
        profile=profile,
        can_preview_private=can_preview_private,
    )
