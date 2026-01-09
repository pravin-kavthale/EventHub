from django.db import connection
from .models import Event, Like,Report
from user.models import Profile

from django.db.models import (
    Exists,
    OuterRef,
    Count,
    Q,
    IntegerField,
    Value,
    Case,
    When,
)

import qrcode
from io import BytesIO

def with_likes(qs, user):
    """
    Annotates queryset with:
    - is_liked (bool for current user)
    - likes_count (total likes)
    """
    qs = qs.annotate(
        likes_count=Count("like", distinct=True)
    )

    if user.is_authenticated:
        return qs.annotate(
            is_liked=Exists(
                Like.objects.filter(
                    user=user,
                    event=OuterRef("pk")
                )
            )
        )

    return qs.annotate(
        is_liked=Value(False, output_field=IntegerField())
    )


def search_events(query, limit=20):
    sql = """
        SELECT id
        FROM "Event_event"
        WHERE search_vector @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(search_vector, plainto_tsquery('english', %s)) DESC
        LIMIT %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [query, query, limit])
        ids = [row[0] for row in cursor.fetchall()]

    if not ids:
        return Event.objects.none()

    preserved_order = Case(
        *[When(id=id, then=pos) for pos, id in enumerate(ids)]
    )

    return (
        Event.objects
        .filter(id__in=ids)
        .select_related('organizer', 'category')
        .order_by(preserved_order)
    )

def generate_qr_code(uuid_value):
    qr=qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(str(uuid_value))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer= BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def check_and_block_event_owner(user):
    flagged_event_count=(
        Event.objects.filter(organizer=user).
        annotate(unique_count=Count('reports', distinct=True))
        .filter(unique_count__gte=5)
        .count()
    )
    if flagged_event_count>=3:
        profile=user.profile
        profile.is_blocked=True
        profile.save(update_fields=["is_blocked"])
        
