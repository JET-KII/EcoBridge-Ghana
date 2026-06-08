import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import WasteType


class TestConfig(TestingConfig):
    SECRET_KEY = "test-secret-key"
    MAIL_DEFAULT_SENDER = "info@ecobridge.services"
    CONTACT_RECIPIENT = "info@ecobridge.services"


@pytest.fixture
def app(tmp_path):
    class LocalTestConfig(TestConfig):
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(LocalTestConfig)

    with app.app_context():
        db.create_all()
        seed_waste_types()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def waste_map(app):
    with app.app_context():
        return {item.name: item.id for item in WasteType.query.order_by(WasteType.name.asc()).all()}


def seed_waste_types():
    for name in ["Plastic", "Paper", "Metal", "Glass"]:
        db.session.add(WasteType(name=name))
    db.session.commit()
