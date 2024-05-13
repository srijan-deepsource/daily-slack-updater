import os

from slack import WebClient
from linear import get_update_to_post

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANEL_ID")

def main():
    update = get_update_to_post()

    if not update:
        # Nothing to post
        return

    slack_client = WebClient(token=SLACK_TOKEN)
    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": update
            },
        }
    ]

    # Send the message:
    blockkit = {"blocks": block}
    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        **blockkit,
        as_user=True,
        unfurl_links=False,
        unfurl_media=False,
    )

if __name__ == "__main__":
    main()
