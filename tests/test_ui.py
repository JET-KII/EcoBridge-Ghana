def test_register_page_includes_password_toggles(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert b"Registration guide" in response.data
    assert b"How to register successfully." in response.data
    assert b"Create the account and check your email" in response.data
    assert response.data.count(b'data-password-toggle="') >= 2
    assert response.data.count(b'class="password-field"') >= 2
    assert response.data.count(b'password-toggle-icon-eye') >= 2
    assert b'password-toggle-label' in response.data


def test_login_page_includes_password_toggle(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b'data-password-toggle="login-password"' in response.data
    assert b'class="password-field"' in response.data
    assert b'password-toggle-icon-eye' in response.data


def test_home_page_includes_story_showcase(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Connecting Waste to Worth" in response.data
    assert b"Service Launch" in response.data
    assert b"Building Partnerships. Driving Circular Solutions. Creating a Cleaner Ghana." in response.data
    assert b'data-showcase-root' in response.data
    assert b'data-showcase-slider' in response.data
    assert response.data.count(b'class="story-showcase-slide"') == 4
    assert response.data.count(b'data-showcase-dot') == 4
    assert b'data-showcase-prev' in response.data
    assert b'data-showcase-next' in response.data
    assert b"Four ideas shaping the EcoBridge Ghana service launch." in response.data
    assert b"ecobridge.services" in response.data
    assert b"info@ecobridge.services" in response.data
    assert b"@ecobridge_ghana" in response.data
    assert b"https://www.instagram.com/ecobridge_ghana?utm_source=qr&amp;igsh=MWFzZGJzZ3MzMTYxOA==" in response.data
    assert b"#ConnectingWasteToWorth" in response.data
    assert b"\xc2\xa9 2026 EcoBridge Ghana. All rights reserved." in response.data


def test_about_page_includes_team_section(client):
    response = client.get("/about")

    assert response.status_code == 200
    assert b"trusted digital marketplace" in response.data
    assert b"Transparency" in response.data
    assert b"Inclusivity" in response.data
    assert b'The people behind EcoBridge Ghana' in response.data
    assert b'data-showcase-root' in response.data
    assert b'data-showcase-slider' in response.data
    assert response.data.count(b'class="story-showcase-slide"') == 9
    assert response.data.count(b'data-showcase-dot') == 9
    assert b'ecobridge-team-group-blurred.png' in response.data
    assert b'ecobridge-team-portrait-future.jpeg' in response.data
    assert b'team-member-01-operation-manager.jpeg' in response.data
    assert b'team-member-02-ceo.jpeg' in response.data
    assert b'team-member-03-portrait.jpeg' in response.data
    assert b'team-member-04-portrait.jpeg' in response.data
    assert b'team-member-06-head-corporate-communications.jpeg' in response.data
    assert b'team-member-07-portrait.jpeg' in response.data
    assert b'team-member-09-portrait.jpeg' in response.data
    assert b'team-member-05-portrait.jpeg' not in response.data
    assert b'team-member-08-portrait.jpeg' not in response.data
    assert b'Previous team slide' in response.data
    assert b'Next team slide' in response.data
    assert b'data-team-image-modal' in response.data
    assert b'team-image-modal-title' in response.data
    assert b"Operation Manager" in response.data
    assert b"CEO" in response.data
    assert b"Head of Corporate Communications" in response.data


def test_contact_page_uses_new_public_identity(client):
    response = client.get("/contact")

    assert response.status_code == 200
    assert b"info@ecobridge.services" in response.data
    assert b"ecobridge.services" in response.data
    assert b"+233 27 328 0091" in response.data
