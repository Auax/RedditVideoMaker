import json
import os.path

import praw

from exceptions import InvalidCredentials
from globals import toml_config


class RedditHandler:
    def __init__(self):
        params = {
            "client_id": toml_config["reddit"]["creds"]["client_id"],
            "client_secret": toml_config["reddit"]["creds"]["client_secret"],
            "username": toml_config["reddit"]["creds"]["username"],
            "password": toml_config["reddit"]["creds"]["password"],
            "user_agent": "Comment Extraction (by u/USERNAME)"
        }

        if not all(params.values()):
            raise InvalidCredentials

        self.reddit = praw.Reddit(**params)

    def extract_comments(self, post_id: str, more_comments_limit: int = 2, max_replies_to_comment: int = 1) -> dict:
        """
        Extract comments of a post
        :param post_id: the ID of the post
        :param more_comments_limit: The maximum number of :class:`.MoreComments` instances to replace.
        :param max_replies_to_comment: the max number of replies to fetch from a comment. If the value is `0`, no replies will be fetched.
        :return: submission_data[dict]
        """
        submission = self.reddit.submission(post_id)

        submission_data = {
            "author": submission.author.name,
            "title": submission.title,
            "score": submission.score,
            "thread_url": "https://www.reddit.com" + submission.permalink,
            "comments": {

            }
        }

        # Removes `MoreComments` obj
        submission.comments.replace_more(limit=more_comments_limit)

        # Iterate through the comments
        for top_level_comment in submission.comments:
            n_of_replies = 0

            if not top_level_comment.author:
                continue

            author_name = top_level_comment.author.name
            # Save the comment to the data obj
            submission_data["comments"][author_name] = {
                "text": top_level_comment.body,
                "score": top_level_comment.score,
                "replies": {}
            }

            if max_replies_to_comment <= 0:
                continue

            # Iterate through the comment replies
            # (note that we will only get the first reply because of the `break` statement)
            for second_level_comment in top_level_comment.replies:
                # Append the replies to the data obj
                submission_data["comments"][author_name]["replies"][
                    second_level_comment.author.name] = {
                    "text": second_level_comment.body,
                    "score": second_level_comment.score
                }

                n_of_replies += 1
                if n_of_replies >= max_replies_to_comment:
                    break

        return submission_data

    def save_json(self, post_id: str, filename: str = "data/results/comments.json", **kwargs) -> dict:
        """
        Get comments
        :param post_id: the ID of the post
        :param filename: if the filename is defined, save comments to file
        :param kwargs: `extract_comments()` other arguments
        :return: comments_data[dict]
        """

        comments_data = self.extract_comments(post_id, **kwargs)

        if not os.path.exists(dirs := os.path.dirname(filename)):
            os.makedirs(dirs)

        if filename:
            with open(filename, "w") as file:
                json.dump(comments_data, file, indent=4)

        return comments_data
