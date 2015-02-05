#!/usr/bin/env python

# Import our facebook python SDK
import facebook
import json # Grab our JSON lib too
import os
import datetime
import random
from time import sleep

# Define our Facebook Access Token
access_token = os.getenv('FB_ACCESS_TOKEN')

if not access_token:
    exit("""ERROR!: You must set an access token.
        Try setting the FB_ACCESS_TOKEN environment variable""")

# Define our "thank you" message
thankyou_messages = [
    'Thank you!! :D',
    'Thanks so much!',
    'Thanks!',
    'Thank you! I appreciate it!'
]

# Define our error-based sleep fallback timer
sleep_time = 1


# Define our ridiculous "birthday" query
def build_birthday_fql(min_date, max_date, limit = 500):
    birthday_fql = ("SELECT post_id, actor_id, target_id, created_time, message, comments, like_info "
                    "FROM stream "
                    "WHERE source_id = me() "
                        "AND filter_key = 'others' "
                        "AND created_time > {} "
                        "AND created_time < {} "
                        "AND actor_id != me() "
                        "AND comments.count = 0 "
                        "AND comments.can_post = 1 "
                        "AND like_info.can_like = 1 "
                        "AND (strpos(message, 'birthday') >= 0 "
                            "OR strpos(message, 'Birthday') >= 0 "
                            "OR strpos(message, 'happy') >= 0 "
                            "OR strpos(message, 'Happy') >= 0) "
                    "LIMIT {}")

    return birthday_fql.format(
        int((min_date - datetime.datetime.utcfromtimestamp(0)).total_seconds()),
        int((max_date - datetime.datetime.utcfromtimestamp(0)).total_seconds()),
        limit
    )


# Create a new GraphAPI instance with our access token
graph = facebook.GraphAPI(access_token)

# Get the user's birthdate
birthdate = datetime.datetime.strptime(
    graph.get_object('me')['birthday'],
    '%m/%d/%Y'
)

# Get the user's birthday with the current year
birthday_current_year = datetime.datetime(
    datetime.datetime.utcnow().year,
    birthdate.month,
    birthdate.day
)

fql = build_birthday_fql(birthday_current_year, datetime.datetime.utcnow(), 100)

# Grab our birthday posts using our FQL query
birthday_posts = graph.fql(fql)

# Report how many posts we found...
print 'Query returned', len(birthday_posts), 'results'
print

# Create a counter, because why not?
posts_responded_to = 0;

# Let's loop through all of our returned posts
for post in birthday_posts:
    # Grab the post's ID
    post_id = post['post_id']

    # Get a random message from the list
    rand_message = random.choice(thankyou_messages)

    try:
        if post['like_info']['user_likes'] != True:
            # "Like" the post
            graph.put_object(post_id, 'likes')

        # Post the comment on the post
        graph.put_object(post_id, 'comments', message=rand_message)

        # Increment our counter..
        posts_responded_to += 1

        # Print to keep track
        print 'The like/comment should have posted for post', post_id
    except facebook.GraphAPIError as e:
        print 'Error on responding to post with message:', e.message
        print 'Sleeping for', sleep_time, 'second(s)'

        # Sleep for a bit to try and keep from getting rate limited
        sleep(sleep_time)

# Let's get this "likes" steez going

# Report how many we've operated on..
print
print 'Responded to', posts_responded_to, 'posts'

# Fin
print 'Done.'
