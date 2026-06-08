from app.models import ContactSubmission, Profile, User
from tests.helpers import create_member, login


def test_admin_can_activate_suspend_and_delete_members(client, app):
    with app.app_context():
        create_member(
            email="admin@example.com",
            phone="+233200000008",
            role=User.Role.ADMIN,
            display_name="Admin User",
            status=Profile.Status.APPROVED,
        )
        suspended = create_member(
            email="suspended-admin@example.com",
            phone="+233200000009",
            role=User.Role.COLLECTOR,
            display_name="Suspended Member",
            status=Profile.Status.SUSPENDED,
        )
        removable = create_member(
            email="remove-me@example.com",
            phone="+233200000010",
            role=User.Role.AGENCY,
            display_name="Delete Me",
            status=Profile.Status.APPROVED,
        )
        suspended_id = suspended.id
        removable_id = removable.id

    login(client, "admin@example.com")

    activate_response = client.post(f"/admin/users/{suspended_id}/activate", follow_redirects=True)
    assert b"now active" in activate_response.data

    suspend_response = client.post(f"/admin/users/{suspended_id}/suspend", follow_redirects=True)
    assert b"has been suspended" in suspend_response.data

    delete_response = client.post(f"/admin/users/{removable_id}/delete", follow_redirects=True)
    assert b"Listing removed" in delete_response.data

    with app.app_context():
        activated_user = User.query.filter_by(email="suspended-admin@example.com").first()
        deleted_user = User.query.filter_by(email="remove-me@example.com").first()
        assert activated_user.profile.status == Profile.Status.SUSPENDED
        assert deleted_user is None


def test_admin_can_switch_member_role(client, app):
    with app.app_context():
        create_member(
            email="admin-role@example.com",
            phone="+233200000016",
            role=User.Role.ADMIN,
            display_name="Admin Role",
            status=Profile.Status.APPROVED,
        )
        collector = create_member(
            email="switch-role@example.com",
            phone="+233200000017",
            role=User.Role.COLLECTOR,
            display_name="Switch Me",
            status=Profile.Status.APPROVED,
        )
        collector_id = collector.id

    login(client, "admin-role@example.com")

    response = client.post(
        f"/admin/users/{collector_id}/role",
        data={"role": "agency"},
        follow_redirects=True,
    )

    assert b"is now a Recycling Agency" in response.data

    with app.app_context():
        switched = User.query.filter_by(email="switch-role@example.com").first()
        assert switched.role == User.Role.AGENCY


def test_admin_users_page_shows_role_switch_actions(client, app):
    with app.app_context():
        create_member(
            email="admin-switch-ui@example.com",
            phone="+233200000018",
            role=User.Role.ADMIN,
            display_name="Admin Switch UI",
            status=Profile.Status.APPROVED,
        )
        collector = create_member(
            email="collector-ui@example.com",
            phone="+233200000019",
            role=User.Role.COLLECTOR,
            display_name="Collector UI",
            status=Profile.Status.APPROVED,
        )
        agency = create_member(
            email="agency-ui@example.com",
            phone="+233200000020",
            role=User.Role.AGENCY,
            display_name="Agency UI",
            status=Profile.Status.APPROVED,
        )
        suspended = create_member(
            email="suspended-ui@example.com",
            phone="+233200000021",
            role=User.Role.COLLECTOR,
            display_name="Suspended UI",
            status=Profile.Status.SUSPENDED,
        )
        collector_id = collector.id
        agency_id = agency.id
        suspended_id = suspended.id

    login(client, "admin-switch-ui@example.com")
    response = client.get("/admin/users")

    assert response.status_code == 200
    assert f'/admin/users/{collector_id}/role'.encode() in response.data
    assert f'/admin/users/{agency_id}/role'.encode() in response.data
    assert f'/admin/users/{suspended_id}/activate'.encode() in response.data
    assert b"Make Agency" in response.data
    assert b"Make Collector" in response.data
    assert b"Activate" in response.data


def test_contact_submissions_show_in_admin_messages_and_email_official_mail(client, app):
    with app.app_context():
        create_member(
            email="admin-contact@example.com",
            phone="+233200000011",
            role=User.Role.ADMIN,
            display_name="Admin Contact",
            status=Profile.Status.APPROVED,
        )

    response = client.post(
        "/contact",
        data={
            "full_name": "Kwame Mensah",
            "email": "kwame@example.com",
            "phone": "+233200000012",
            "message": "We would like to discuss a recycling partnership in the Greater Accra region.",
        },
        follow_redirects=True,
    )
    assert b"Thanks for reaching out" in response.data

    with app.app_context():
        saved = ContactSubmission.query.filter_by(email="kwame@example.com").first()
        assert saved is not None

    outbox = app.extensions["mail_outbox"]
    assert len(outbox) == 1
    assert outbox[0]["To"] == app.config["CONTACT_RECIPIENT"]
    assert outbox[0]["Reply-To"] == "kwame@example.com"
    assert "Kwame Mensah" in outbox[0].get_content()

    login(client, "admin-contact@example.com")
    messages_response = client.get("/admin/messages")
    assert b"Kwame Mensah" in messages_response.data
    assert b"recycling partnership" in messages_response.data


def test_suspended_members_show_activate_action_instead_of_suspend(client, app):
    with app.app_context():
        create_member(
            email="admin-ui@example.com",
            phone="+233200000013",
            role=User.Role.ADMIN,
            display_name="Admin UI",
            status=Profile.Status.APPROVED,
        )
        active_member = create_member(
            email="active-ui@example.com",
            phone="+233200000014",
            role=User.Role.AGENCY,
            display_name="Active Listing",
            status=Profile.Status.APPROVED,
        )
        suspended_member = create_member(
            email="suspended-ui-alt@example.com",
            phone="+233200000015",
            role=User.Role.COLLECTOR,
            display_name="Suspended Listing",
            status=Profile.Status.SUSPENDED,
        )
        active_id = active_member.id
        suspended_id = suspended_member.id

    login(client, "admin-ui@example.com")
    response = client.get("/admin/users")

    assert response.status_code == 200
    assert f'/admin/users/{suspended_id}/activate'.encode() in response.data
    assert f'/admin/users/{active_id}/activate'.encode() not in response.data
