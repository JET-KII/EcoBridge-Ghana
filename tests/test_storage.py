from app.models import Profile


def test_profile_image_src_uses_local_static_url(app):
    profile = Profile(image_filename="profile.png")

    with app.test_request_context():
        assert profile.image_src == "/static/uploads/profile.png"


def test_profile_image_src_keeps_remote_blob_url(app):
    url = "https://example.public.blob.vercel-storage.com/profiles/profile.png"
    profile = Profile(image_filename=url)

    with app.test_request_context():
        assert profile.image_src == url
