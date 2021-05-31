from django.test.testcases import TestCase
from mock import patch, Mock, call

from utils.image_generator import generate_from_blob


class ImageGeneratorTestCase(TestCase):
    @patch('utils.image_generator.Image')
    def test_generate_from_url(self, mock_image):
        returned_blob = 'returned_blob'
        mock_sequence = 'sequence_0'
        mock_sample = Mock()
        mock_make_blob = Mock(return_value=returned_blob)
        mock_image_sequences_return = Mock(__enter__=Mock(return_value=mock_sequence), __exit__=Mock())

        mock_image_class_2_return = Mock(sample=mock_sample, make_blob=mock_make_blob)
        mock_image_sequences = Mock(sequence=[mock_image_sequences_return])

        mock_image_class_1 = Mock(__enter__=Mock(return_value=mock_image_sequences), __exit__=Mock())
        mock_image_class_2 = Mock(__enter__=Mock(return_value=mock_image_class_2_return), __exit__=Mock())
        mock_image.side_effect = [mock_image_class_1, mock_image_class_2]

        blob = 'blob'
        image_generated = generate_from_blob(blob)

        image_calls = [call(blob=blob, resolution=500), call('sequence_0')]
        mock_image.assert_has_calls(image_calls)
        mock_sample.assert_called_with(850, 1100)
        mock_make_blob.assert_called_with('jpeg')

        assert image_generated == returned_blob

    @patch('utils.image_generator.Image')
    def test_generate_from_url_fail(self, mock_image):
        mock_image.return_value = Mock(__enter__=Exception('any error'), __exit__=Mock())

        blob = 'blob'
        image_generated = generate_from_blob(blob)

        assert image_generated is None
