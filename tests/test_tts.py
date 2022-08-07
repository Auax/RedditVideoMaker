import os.path
import unittest

from creator import TikTokTTS


class TtsTest(unittest.TestCase):
    def test_invalid_text(self):
        # This text has no "." delimiting the sentences
        string = "Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello" * 5
        filename = "test.mp3"

        tts = TikTokTTS()
        success = tts.run(string, filename)

        self.assertFalse(success)  # The operation has to fail since the text has no splitting options

    def test_valid_text(self):
        string = "Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello Hello." * 5
        filename = "test.mp3"

        tts = TikTokTTS()
        tts.run(string, filename)

        filesize = os.path.getsize(filename)
        self.assertGreater(filesize, 0)

        try:
            os.remove(filename)
        except Exception:
            pass


if __name__ == '__main__':
    unittest.main()
