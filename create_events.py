import random
from django.contrib.auth.models import User
from Event.models import Event
from Event.models import Like, Comment, EventRegistration

users = list(User.objects.all())
events = list(Event.objects.all())

comment_samples = [
    "This event looks amazing!",
    "Can't wait to attend this!",
    "Really excited for this event.",
    "Hope to meet great people here.",
    "This will be a great learning opportunity.",
    "Looking forward to this!",
    "Amazing lineup!",
    "This event will be fantastic.",
    "I attended last year and it was great.",
    "Highly recommended!"
]

likes_created = 0
registrations_created = 0
comments_created = 0

for event in events:

    # Random Likes
    like_users = random.sample(users, random.randint(2, min(8, len(users))))
    for user in like_users:
        like, created = Like.objects.get_or_create(user=user, event=event)
        if created:
            likes_created += 1

    # Random Registrations
    reg_users = random.sample(users, random.randint(1, min(6, len(users))))
    for user in reg_users:
        reg, created = EventRegistration.objects.get_or_create(user=user, event=event)
        if created:
            registrations_created += 1

    # Random Comments
    comment_users = random.sample(users, random.randint(2, min(6, len(users))))
    for user in comment_users:
        comment = Comment.objects.create(
            user=user,
            event=event,
            content=random.choice(comment_samples)
        )
        comments_created += 1

        # Random Replies
        if random.choice([True, False]):
            reply_user = random.choice(users)
            Comment.objects.create(
                user=reply_user,
                event=event,
                parent=comment,
                content="Reply: " + random.choice(comment_samples)
            )
            comments_created += 1


print("Likes created:", likes_created)
print("Registrations created:", registrations_created)
print("Comments created:", comments_created)
print("Interaction data created successfully!")