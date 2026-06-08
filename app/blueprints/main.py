from flask import Blueprint, current_app, make_response, render_template, request, url_for
from sqlalchemy import func

from ..content import ABOUT_FOUNDATION, ABOUT_TEAM, HOME_CAMPAIGN, HOME_SHOWCASE_ITEMS
from ..extensions import db
from ..forms import ContactForm
from ..mailer import send_email
from ..models import ContactSubmission, Profile, User, WasteType


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    public_profiles = (
        db.session.query(func.count(Profile.id))
        .join(User)
        .filter(Profile.status != Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)
        .scalar()
    )
    agency_count = (
        db.session.query(func.count(Profile.id))
        .join(User)
        .filter(Profile.status != Profile.Status.SUSPENDED, User.role == User.Role.AGENCY)
        .scalar()
    )
    collector_count = (
        db.session.query(func.count(Profile.id))
        .join(User)
        .filter(Profile.status != Profile.Status.SUSPENDED, User.role == User.Role.COLLECTOR)
        .scalar()
    )
    waste_type_count = WasteType.query.count()

    featured_profiles = (
        Profile.query.join(User)
        .filter(Profile.status != Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)
        .order_by(Profile.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "main/home.html",
        page_title="Connecting Waste to Worth",
        meta_description=(
            "EcoBridge Ghana service launch connecting waste to worth through trusted "
            "partnerships, circular plastic recovery, and cleaner recycling connections in Ghana."
        ),
        public_profiles=public_profiles,
        agency_count=agency_count,
        collector_count=collector_count,
        waste_type_count=waste_type_count,
        featured_profiles=featured_profiles,
        home_campaign=HOME_CAMPAIGN,
        home_showcase_items=HOME_SHOWCASE_ITEMS,
    )


@main_bp.get("/about")
def about():
    return render_template(
        "main/about.html",
        page_title="About EcoBridge Ghana",
        meta_description=(
            "Learn about EcoBridge Ghana's mission, vision, and core values for building "
            "a trusted digital marketplace for recyclable materials in Africa."
        ),
        about_foundation=ABOUT_FOUNDATION,
        about_team=ABOUT_TEAM,
    )


@main_bp.get("/services")
def services():
    return render_template(
        "main/services.html",
        page_title="Services",
        meta_description="Explore EcoBridge Ghana services for collectors, recyclers, and sustainability partners.",
    )


@main_bp.get("/education")
def education():
    return render_template(
        "main/education.html",
        page_title="Waste Management Education",
        meta_description="Practical waste management tips, sorting guidance, and circular economy education from EcoBridge Ghana.",
    )


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        submission = ContactSubmission(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip() if form.phone.data else "",
            message=form.message.data.strip(),
        )
        db.session.add(submission)
        db.session.commit()
        recipient_email = current_app.config["CONTACT_RECIPIENT"]
        email_sent = send_email(
            recipients=recipient_email,
            subject=f"New EcoBridge Ghana contact message from {submission.full_name}",
            reply_to=submission.email,
            body=(
                "A new message has been submitted through the EcoBridge Ghana contact form.\n\n"
                f"Name: {submission.full_name}\n"
                f"Email: {submission.email}\n"
                f"Phone: {submission.phone or 'Not provided'}\n\n"
                "Message:\n"
                f"{submission.message}\n"
            ),
        )
        return render_template(
            "main/contact_success.html",
            page_title="Message Sent",
            meta_description="Your message has been sent to EcoBridge Ghana.",
            email_sent=email_sent,
            recipient_email=recipient_email,
        )

    return render_template(
        "main/contact.html",
        page_title="Contact EcoBridge Ghana",
        meta_description="Send a message to EcoBridge Ghana to join the recycling network or discuss partnership opportunities.",
        form=form,
    )


@main_bp.get("/robots.txt")
def robots():
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {request.url_root.rstrip('/')}{url_for('main.sitemap')}",
        ]
    )
    return current_app.response_class(body, mimetype="text/plain")


@main_bp.get("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    urls = [
        f"{base}{url_for('main.home')}",
        f"{base}{url_for('main.about')}",
        f"{base}{url_for('main.services')}",
        f"{base}{url_for('main.education')}",
        f"{base}{url_for('main.contact')}",
        f"{base}{url_for('directory.search')}",
        f"{base}{url_for('auth.register')}",
    ]
    urls.extend(
        f"{base}{url_for('directory.detail', profile_id=profile.id)}"
        for profile in (
            Profile.query.join(User)
            .filter(Profile.status != Profile.Status.SUSPENDED, User.role != User.Role.ADMIN)
            .all()
        )
    )
    xml = render_template("main/sitemap.xml", urls=urls)
    response = make_response(xml)
    response.mimetype = "application/xml"
    return response
