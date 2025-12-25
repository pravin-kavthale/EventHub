from Event.models import Event
from django.db import connection

def search_events(query, limit=20):
    sql = """
        SELECT id
        FROM (
            SELECT id,
                   ts_rank(
                       to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,'')),
                       plainto_tsquery('english', %s)
                   ) AS rank
            FROM "Event_event"
        ) AS ranked
        WHERE rank > 0
        ORDER BY rank DESC
        LIMIT %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [query, limit])
        ids = [row[0] for row in cursor.fetchall()]
    
    return Event.objects.filter(id__in=ids).select_related('organizer', 'category')
