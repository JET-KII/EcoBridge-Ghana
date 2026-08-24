import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import WasteType


DEFAULT_WASTE_TYPES = [
    "Plastic",
    "Paper",
    "Metal",
    "Glass",
    "Organic",
    "Electronic Waste",
    "Textiles",
]


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        existing = {item.name for item in WasteType.query.all()}
        for waste_name in DEFAULT_WASTE_TYPES:
            if waste_name not in existing:
                db.session.add(WasteType(name=waste_name))
        db.session.commit()
    print("Database initialized.")


if __name__ == "__main__":
    main()
