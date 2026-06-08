from app.models import Profile, User
from tests.helpers import create_member, login


def test_directory_shows_active_and_legacy_profiles_but_hides_suspended(client, app):
    with app.app_context():
        create_member(
            email="active@example.com",
            phone="+233200000003",
            role=User.Role.COLLECTOR,
            display_name="Active Collector",
            status=Profile.Status.APPROVED,
        )
        create_member(
            email="legacy@example.com",
            phone="+233200000004",
            role=User.Role.AGENCY,
            display_name="Legacy Agency",
            status=Profile.Status.PENDING,
        )
        create_member(
            email="suspended@example.com",
            phone="+233200000022",
            role=User.Role.AGENCY,
            display_name="Suspended Agency",
            status=Profile.Status.SUSPENDED,
        )

    response = client.get("/directory/")

    assert b"Active Collector" in response.data
    assert b"Legacy Agency" in response.data
    assert b"Suspended Agency" not in response.data


def test_directory_filters_by_location_role_and_waste_type(client, app, waste_map):
    with app.app_context():
        create_member(
            email="accra@example.com",
            phone="+233200000005",
            role=User.Role.COLLECTOR,
            display_name="Accra Plastics",
            city="Accra",
            waste_names=["Plastic"],
            status=Profile.Status.APPROVED,
        )
        create_member(
            email="kumasi@example.com",
            phone="+233200000006",
            role=User.Role.AGENCY,
            display_name="Kumasi Metals",
            region="Ashanti",
            city="Kumasi",
            waste_names=["Metal"],
            status=Profile.Status.APPROVED,
        )

    response = client.get(f"/directory/?location=Kumasi&user_type=agency&waste_type={waste_map['Metal']}")

    assert b"Kumasi Metals" in response.data
    assert b"Accra Plastics" not in response.data


def test_private_profile_preview_visible_to_owner_for_suspended_listing(client, app):
    with app.app_context():
        user = create_member(
            email="owner@example.com",
            phone="+233200000007",
            role=User.Role.COLLECTOR,
            display_name="Owner Listing",
            status=Profile.Status.SUSPENDED,
        )
        profile_id = user.profile.id

    anonymous_response = client.get(f"/directory/{profile_id}")
    assert anonymous_response.status_code == 404

    login(client, "owner@example.com")
    owner_response = client.get(f"/directory/{profile_id}")
    assert owner_response.status_code == 200
    assert b"Private preview" in owner_response.data
