from app.models import Profile, User
from tests.helpers import create_member, login


def test_register_creates_active_profile_and_sends_email(client, app, waste_map):
    response = client.post(
        "/register",
        data={
            "display_name": "Green Routes Ltd",
            "role": "collector",
            "phone": "+233201112233",
            "email": "collector@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "region": "Greater Accra",
            "city": "Accra",
            "area": "Dansoman",
            "waste_types": [waste_map["Plastic"], waste_map["Paper"]],
            "description": "We aggregate recyclable plastic and paper from households and small businesses.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"account is active" in response.data
    assert b"confirmation email has been sent" in response.data

    with app.app_context():
        user = User.query.filter_by(email="collector@example.com").first()
        assert user is not None
        assert user.role == User.Role.COLLECTOR
        assert user.profile.status == Profile.Status.APPROVED
        assert {item.name for item in user.profile.waste_types} == {"Plastic", "Paper"}

    outbox = app.extensions["mail_outbox"]
    assert len(outbox) == 1
    assert outbox[0]["To"] == "collector@example.com"
    assert "account is ready" in outbox[0]["Subject"].lower()
    assert "created successfully" in outbox[0].get_content()


def test_register_rejects_duplicate_email(client, app):
    with app.app_context():
        create_member(
            email="duplicate@example.com",
            phone="+233200000001",
            role=User.Role.COLLECTOR,
            display_name="Duplicate Listing",
        )

    response = client.post(
        "/register",
        data={
            "display_name": "Another Listing",
            "role": "collector",
            "phone": "+233201112244",
            "email": "duplicate@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "region": "Greater Accra",
            "city": "Accra",
            "area": "Osu",
            "waste_types": [1],
            "description": "We recover recyclable materials and route them to trusted recycling partners.",
        },
    )

    assert b"already exists" in response.data


def test_login_logout_and_profile_edit_flow(client, app):
    with app.app_context():
        create_member(
            email="member@example.com",
            phone="+233200000002",
            role=User.Role.AGENCY,
            display_name="Agency One",
            status=Profile.Status.APPROVED,
        )

    login_response = login(client, "member@example.com")
    assert b"Welcome back" in login_response.data

    update_response = client.post(
        "/profile/edit",
        data={
            "display_name": "Agency One Updated",
            "phone": "+233200000099",
            "email": "member@example.com",
            "region": "Ashanti",
            "city": "Kumasi",
            "area": "Asokwa",
            "waste_types": [1],
            "description": "We process recyclable material from multiple municipal and community collection sources.",
        },
        follow_redirects=True,
    )

    assert b"profile has been updated" in update_response.data

    with app.app_context():
        user = User.query.filter_by(email="member@example.com").first()
        assert user.phone == "+233200000099"
        assert user.profile.city == "Kumasi"

    logout_response = client.post("/logout", follow_redirects=True)
    assert b"signed out" in logout_response.data
