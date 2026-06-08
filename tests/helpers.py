from app.extensions import db
from app.models import Profile, User, WasteType


def create_member(
    *,
    email,
    phone,
    role,
    display_name,
    region="Greater Accra",
    city="Accra",
    area="Airport",
    description="We coordinate recovery logistics and recycling support across communities.",
    status=Profile.Status.APPROVED,
    waste_names=None,
):
    waste_names = waste_names or ["Plastic"]
    user = User(email=email, phone=phone, role=role)
    user.set_password("Password123!")
    profile = Profile(
        display_name=display_name,
        region=region,
        city=city,
        area=area,
        description=description,
        status=status,
    )
    profile.waste_types = WasteType.query.filter(WasteType.name.in_(waste_names)).all()
    user.profile = profile
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password="Password123!"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
