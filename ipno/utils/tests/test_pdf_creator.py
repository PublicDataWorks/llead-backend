from datetime import datetime

from django.test.testcases import TestCase
from mock import patch, Mock, MagicMock

from utils.constants import BASE_MARGIN, PAGE_NUMBER, PAGE_SIZE, SPACER, PAGE_NUMBER_FONT
from utils.pdf_creator import ArticlePdfCreator


class ArticlePdfCreatorTestCase(TestCase):
    def setUp(self):
        self.title = 'Title'
        self.author = 'Author'
        self.date = datetime.now().date()
        self.content = [{
                'style': 'BodyText',
                'content': "This is first paragraph. You can see it."
            },
            {
                'style': 'Heading4',
                'content': "This is subtitle"
            },
            {
                'style': 'BodyText',
                'content': "This is the second one. You can see it, too."
            },
        ]

        self.link = '/link'

        self.test_date = self.date
        self.pdf = ArticlePdfCreator(
            self.title,
            self.author,
            self.date,
            self.content,
            self.link
        )

    def test_add_page_number_fake(self):
        canvas = MagicMock()
        doc = MagicMock(
            page=1
        )
        self.pdf.add_page_number(canvas, doc)

        canvas.saveState.assert_called()
        canvas.setFont.assert_called_with(
            PAGE_NUMBER_FONT['TYPE'],
            PAGE_NUMBER_FONT['SIZE'],
        )
        canvas.drawCentredString.assert_called_with(
            PAGE_NUMBER['x'],
            PAGE_NUMBER['y'],
            '1'
        )
        canvas.restoreState.assert_called()

    @patch('utils.pdf_creator.Paragraph')
    def test_build_body(self, mock_paragraph):
        def mock_paragraph_side_effect(paragraph_text, paragraph_style):
            return {
                'text': paragraph_text,
                'style': paragraph_style
            }
        mock_paragraph.side_effect = mock_paragraph_side_effect

        def mock_get_style_side_effect(style):
            return style
        self.pdf.get_style = MagicMock(side_effect=mock_get_style_side_effect)

        body = self.pdf.build_body()

        assert body == [
            {
                'text': "This is first paragraph. You can see it.",
                'style': "BodyText"
            },
            {
                'text': "This is subtitle",
                'style': "Heading4"
            },
            {
                'text': "This is the second one. You can see it, too.",
                'style': "BodyText"
            },
        ]

    @patch('utils.pdf_creator.getSampleStyleSheet')
    def test_get_style(self, mock_get_sample_style_sheet):
        mock_style_body_text = Mock()
        mock_style_heading_1 = Mock()
        mock_sample_style_sheet = {
            'BodyText': mock_style_body_text,
            'Heading1': mock_style_heading_1,
        }
        mock_get_sample_style_sheet.return_value = mock_sample_style_sheet

        heading_1_style = self.pdf.get_style('Heading1')
        assert heading_1_style == mock_style_heading_1

        meta_style = self.pdf.get_style('BodyText', {'fontSize': 11})
        assert meta_style == mock_style_body_text
        assert mock_style_body_text.fontSize == 11

    @patch('utils.pdf_creator.Spacer')
    @patch('utils.pdf_creator.Paragraph')
    @patch('utils.pdf_creator.SimpleDocTemplate')
    @patch('utils.pdf_creator.BytesIO')
    def test_build_pdf_flow(
            self,
            mock_byte_io,
            mock_simple_doc_template,
            mock_paragraph,
            mock_spacer,
    ):
        mock_buffer_get_value = Mock(return_value='byte-io-getvalue')
        mock_buffer_close = Mock()
        mock_byte_io_object = Mock(
            getvalue=mock_buffer_get_value,
            close=mock_buffer_close,
        )
        mock_byte_io.return_value = mock_byte_io_object

        mock_multi_build = Mock()
        mock_simple_doc_template_object = Mock(
            multiBuild=mock_multi_build
        )
        mock_simple_doc_template.return_value = mock_simple_doc_template_object

        def mock_paragraph_side_effect(paragraph_text, paragraph_style):
            return {
                'text': paragraph_text,
                'style': paragraph_style
            }
        mock_paragraph.side_effect = mock_paragraph_side_effect

        def mock_spacer_side_effect(x, y):
            return f'spacer[{x}][{y}]'
        mock_spacer.side_effect = mock_spacer_side_effect

        def mock_get_style_side_effect(style_name, custom_style={}):
            custom_style_list = [f'{key}-{value}' for key, value in custom_style.items()]
            custom_style_str = ','.join(custom_style_list)
            return f'{style_name},{custom_style_str}'
        mock_get_style = Mock()
        mock_get_style.side_effect = mock_get_style_side_effect
        self.pdf.get_style = mock_get_style

        mock_add_page_number = Mock()
        self.pdf.add_page_number = mock_add_page_number

        mock_build_body = Mock(return_value=['body1', 'body2'])
        self.pdf.build_body = mock_build_body

        buffer = self.pdf.build_pdf()

        mock_simple_doc_template.assert_called_with(
            mock_byte_io_object,
            pagesize=PAGE_SIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN * 2
        )

        expected_flows = [
            {
                'text': 'Title',
                'style': 'Heading1,',
            },
            {
                'text': 'Author',
                'style': "BodyText,fontSize-11",
            },
            {
                'text': f'Date: {self.test_date.strftime("%m/%d/%Y")}',
                'style': "BodyText,fontSize-11",
            },
            {
                'text': 'Source URL: <link href="/link">/link</link>',
                'style': "BodyText,fontSize-11",
            },
            f'spacer[{SPACER["x"]}][{SPACER["y"]}]',
            'body1',
            'body2'
        ]
        mock_multi_build.assert_called_with(
            expected_flows,
            onFirstPage=mock_add_page_number,
            onLaterPages=mock_add_page_number,
        )
        mock_buffer_get_value.assert_called()
        mock_buffer_close.assert_called()

        assert buffer == 'byte-io-getvalue'

    @patch('utils.pdf_creator.Spacer')
    @patch('utils.pdf_creator.Paragraph')
    @patch('utils.pdf_creator.SimpleDocTemplate')
    @patch('utils.pdf_creator.BytesIO')
    def test_build_pdf_flow_without_author(
            self,
            mock_byte_io,
            mock_simple_doc_template,
            mock_paragraph,
            mock_spacer,
    ):
        self.pdf_without_author = ArticlePdfCreator(
            self.title,
            None,
            self.date,
            self.content,
            self.link
        )

        mock_buffer_get_value = Mock(return_value='byte-io-getvalue')
        mock_buffer_close = Mock()
        mock_byte_io_object = Mock(
            getvalue=mock_buffer_get_value,
            close=mock_buffer_close,
        )
        mock_byte_io.return_value = mock_byte_io_object

        mock_multi_build = Mock()
        mock_simple_doc_template_object = Mock(
            multiBuild=mock_multi_build
        )
        mock_simple_doc_template.return_value = mock_simple_doc_template_object

        def mock_paragraph_side_effect(paragraph_text, paragraph_style):
            return {
                'text': paragraph_text,
                'style': paragraph_style
            }

        mock_paragraph.side_effect = mock_paragraph_side_effect

        def mock_spacer_side_effect(x, y):
            return f'spacer[{x}][{y}]'

        mock_spacer.side_effect = mock_spacer_side_effect

        def mock_get_style_side_effect(style_name, custom_style={}):
            custom_style_list = [f'{key}-{value}' for key, value in custom_style.items()]
            custom_style_str = ','.join(custom_style_list)
            return f'{style_name},{custom_style_str}'

        mock_get_style = Mock()
        mock_get_style.side_effect = mock_get_style_side_effect
        self.pdf_without_author.get_style = mock_get_style

        mock_add_page_number = Mock()
        self.pdf_without_author.add_page_number = mock_add_page_number

        mock_build_body = Mock(return_value=['body1', 'body2'])
        self.pdf_without_author.build_body = mock_build_body

        buffer = self.pdf_without_author.build_pdf()

        mock_simple_doc_template.assert_called_with(
            mock_byte_io_object,
            pagesize=PAGE_SIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN * 2
        )

        expected_flows = [
            {
                'text': 'Title',
                'style': 'Heading1,',
            },
            {
                'text': f'Date: {self.test_date.strftime("%m/%d/%Y")}',
                'style': "BodyText,fontSize-11",
            },
            {
                'text': 'Source URL: <link href="/link">/link</link>',
                'style': "BodyText,fontSize-11",
            },
            f'spacer[{SPACER["x"]}][{SPACER["y"]}]',
            'body1',
            'body2'
        ]
        mock_multi_build.assert_called_with(
            expected_flows,
            onFirstPage=mock_add_page_number,
            onLaterPages=mock_add_page_number,
        )
        mock_buffer_get_value.assert_called()
        mock_buffer_close.assert_called()

        assert buffer == 'byte-io-getvalue'
