import unittest
import img_process

class SideCheckMethods(unittest.TestCase):
    def test_widthCheck(self):
        img = img_process.widthImg # Replace with the actual class or object you're testing
        self.assertEqual(img, 1200)  # Assuming width is an attribute of img_process

    def test_heightCheck(self):
        img = img_process.heightImg # Replace with the actual class or object you're testing
        self.assertEqual(img, 1600)  # Assuming height is an attribute of imageOpen

if __name__ == '__main__':
    unittest.main()