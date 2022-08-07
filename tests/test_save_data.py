import os.path
import unittest

from reddit_api import RedditHandler


class DataTest(unittest.TestCase):
    def test_save_data(self):
        reddit_handler = RedditHandler()
        filename = "test.json"
        data = reddit_handler.save_json(post_id="wgktou",
                                        filename=filename,
                                        more_comments_limit=0,
                                        max_replies_to_comment=1)
        exists = os.path.exists(filename)
        self.assertTrue((exists and data))

        try:
            os.remove(filename)
        except Exception:
            pass


if __name__ == '__main__':
    unittest.main()
