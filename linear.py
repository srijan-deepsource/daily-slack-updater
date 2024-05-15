
import requests
from datetime import datetime, timedelta, timezone
from textwrap import dedent
import os

# Get the API key from the environment
API_KEY = os.environ.get('LINEAR_API_KEY')
if not API_KEY:
    raise ValueError('No LINEAR_API_KEY found in the environment')

VIEW_ID = os.environ.get('LINEAR_VIEW_ID')
if not VIEW_ID:
    raise ValueError('No LINEAR_VIEW_ID found in the environment')


def get_issues_from_view(view_id):
    # Also filter issue where updatedAt is greater than past 1 day
    query = """
    query Query {
      customView(id: "%s") {
        issues(
            includeArchived: false
            orderBy: updatedAt
        ) {
          nodes {
            updatedAt
            completedAt
            state {
              name
            }
            priority
            identifier
            title
            url
          }
        }
      }
    }
    """ % view_id

    # Set the headers
    headers = {
        'Authorization': f'{API_KEY}',
        'Content-Type': 'application/json'
    }

    # Make the request
    response = requests.post(
        'https://api.linear.app/graphql',
        json={'query': query},
        headers=headers

    )
    issues = response.json()

    # # Now, filter out issues by state.
    # # Done, In progress, and Todo
    done = []
    in_progress = []
    todo = []
    for issue in issues['data']['customView']['issues']['nodes']:
        if issue['state']['name'] == 'Done':
            # Only care about issues that are done in the last 24 hours.
            # So, get the current time in ISO 8601, UTC
            # and add it to done if delta is less than 24 hours.
            current_time = datetime.now(timezone.utc)
            completed_at = datetime.strptime(issue['completedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            completed_at = updated_at.replace(tzinfo=timezone.utc)
            delta = current_time - completed_at
            if delta < timedelta(hours=24):
                # Done in the last 24 hours.
                done.append(issue)
        elif issue['state']['name'] in ('In Progress', 'In Review'):
            in_progress.append(issue)
        else:
            todo.append(issue)

    return done, in_progress, todo


def get_update_to_post():
    done, in_progress, _ = get_issues_from_view(VIEW_ID)
    # Create the update
    newline = '\n'
    update_message = ''
    if len(done) > 0:
        update_message += dedent(
            f"""*Done* 🎉
{''.join([f" - <{issue['url']}|{issue['title']}>{newline}" for issue in done])}
        """)
    if len(in_progress) > 0:
        update_message += dedent(f"""*In Progress* 👷‍♂️
{''.join([f" - <{issue['url']}|{issue['title']}>{newline}" for issue in in_progress])}
        """)

    return update_message
