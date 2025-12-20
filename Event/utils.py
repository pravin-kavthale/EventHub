from django.db import connection
from .models import Event 

def search_events(query, limit=20):
    sql = """
        SELECT e.id, bm25(Event_event_fts, 10.0, 6.0, 3.0) AS rank
        FROM Event_event e
        JOIN Event_event_fts
            ON e.id = Event_event_fts.rowid
        WHERE Event_event_fts MATCH %s
        ORDER BY rank
        LIMIT %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [query, limit])
        ids = [row[0] for row in cursor.fetchall()]
    # Fetch full Event objects including related fields
    return Event.objects.filter(id__in=ids).select_related('organizer', 'category')
