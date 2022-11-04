from PIL.Image import Resampling


from django.conf import settings
from django.test.testcases import TestCase

import pytest
from mock import patch, Mock, call
from unittest.mock import MagicMock


from utils.constants import MAP_DOT_SHARPNESS, MAP_DOT_RADIUS, LA_LOC_TOP_LEFT, LA_LOC_BOTTOM_RIGHT
from utils.image_generator import generate_from_blob, generate_dot_img, generate_map_thumbnail


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

    @patch('PIL.Image.new')
    @patch('PIL.ImageDraw.Draw')
    def test_generate_dot_img(self,  mock_draw, mock_new_image):
        mock_draw_return = MagicMock()
        mock_draw.return_value = mock_draw_return

        mock_new_image_return = MagicMock()
        mock_new_image.return_value = mock_new_image_return

        img_width = 150
        img_height = 300
        base_image_info = (img_width, img_height)
        dot_x = 15
        dot_y = 50
        dot_location = (dot_x, dot_y)

        dot_image_return = 'dot-image-return'
        mock_new_image_return.resize.return_value = dot_image_return

        result = generate_dot_img(base_image_info, dot_location)

        mock_new_image.assert_called_with(
            'RGBA',
            (img_width * MAP_DOT_SHARPNESS, img_height * MAP_DOT_SHARPNESS),
            (255, 255, 255, 0)
        )

        mock_draw.assert_called_with(
            mock_new_image_return
        )

        expected_upper_left_ellipse = (
            MAP_DOT_SHARPNESS * (dot_x - MAP_DOT_RADIUS),
            MAP_DOT_SHARPNESS * (dot_y - MAP_DOT_RADIUS)
        )
        expected_bottom_right_ellipse = (
            MAP_DOT_SHARPNESS * (dot_x + MAP_DOT_RADIUS),
            MAP_DOT_SHARPNESS * (dot_y + MAP_DOT_RADIUS)
        )

        mock_draw_return.ellipse.assert_called_with(
            [expected_upper_left_ellipse, expected_bottom_right_ellipse],
            fill='black'
        )
        mock_new_image_return.resize.assert_called_with(
            base_image_info,
            Resampling.LANCZOS
        )

        assert result == dot_image_return

    @patch('utils.image_generator.generate_dot_img')
    @patch('utils.image_generator.BytesIO')
    @patch('PIL.Image.alpha_composite')
    @patch('PIL.Image.open')
    def test_generate_map_thumbnail_success(
            self,
            mock_open_image,
            mock_alpha_composite,
            mock_byte_io,
            mock_generate_dot_img
    ):
        mock_open_image_return = MagicMock()
        base_img_width = 128
        base_img_height = 256
        base_image = MagicMock(
            width=base_img_width,
            height=base_img_height,
        )
        mock_open_image_return.__enter__.return_value = base_image
        mock_open_image.return_value = mock_open_image_return

        mock_alpha_composite_return = MagicMock()
        mock_alpha_composite.return_value = mock_alpha_composite_return

        mock_byte_io_object = MagicMock()
        expected_map_bytes = 'map-bytes'
        mock_byte_io_object.getvalue.return_value = expected_map_bytes
        mock_byte_io.return_value = mock_byte_io_object

        dot_img_return = 'dot-image-return'
        mock_generate_dot_img.return_value = dot_img_return

        map_lng = -91.2440566
        map_lat = 30.385919

        generated_map = generate_map_thumbnail(map_lng, map_lat)

        mock_open_image.assert_called_with(f'{settings.BASE_DIR}/map.png')

        dot_x = (map_lng - LA_LOC_TOP_LEFT[0]) / (LA_LOC_BOTTOM_RIGHT[0] - LA_LOC_TOP_LEFT[0]) * base_img_width
        dot_y = (map_lat - LA_LOC_TOP_LEFT[1]) / (LA_LOC_BOTTOM_RIGHT[1] - LA_LOC_TOP_LEFT[1]) * base_img_height

        mock_generate_dot_img.assert_called_with(
            (base_img_width, base_img_height),
            (dot_x, dot_y)
        )
        mock_alpha_composite.assert_called_with(
            base_image,
            dot_img_return
        )

        mock_byte_io.assert_called()
        mock_alpha_composite_return.save.assert_called_with(
            mock_byte_io_object,
            format='PNG'
        )
        mock_byte_io_object.getvalue.assert_called()
        mock_byte_io_object.close.assert_called()

        assert generated_map == expected_map_bytes

    def test_generate_map_thumbnail_invalid_long(self):
        invalid_map_lng = -150.2440566
        map_lat = 30.385919

        with pytest.raises(ValueError, match=f'Invalid longitude {invalid_map_lng}'):
            generate_map_thumbnail(invalid_map_lng, map_lat)

    def test_generate_map_thumbnail_invalid_lat(self):
        map_lng = -91.2440566
        invalid_map_lat = 50.385919

        with pytest.raises(ValueError, match=f'Invalid latitude {invalid_map_lat}'):
            generate_map_thumbnail(map_lng, invalid_map_lat)
