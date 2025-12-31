from django.db import connection
from Event.models import Event

from django.db.models import Case, When

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
