from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import letter

from utils.constants import (
    BASE_MARGIN,
    PAGE_NUMBER,
    PAGE_NUMBER_FONT,
    PAGE_SIZE,
    SPACER,
)


class ArticlePdfCreator:
    def __init__(self, title, author, date, content, link):
        self.title = title
        self.author = author
        self.date = date
        self.content = content
        self.link = link

    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(
            PAGE_NUMBER_FONT["TYPE"],
            PAGE_NUMBER_FONT["SIZE"],
        )
        canvas.drawCentredString(PAGE_NUMBER["x"], PAGE_NUMBER["y"], str(doc.page))
        canvas.restoreState()

    def build_body(self):
        body = [
            Paragraph(
                paragraph["content"].replace("\n", "<br/>"),
                self.get_style(paragraph["style"]),
            )
            for paragraph in self.content
        ]

        return body

    def get_style(self, style_name, custom_style={}):
        sample_style_sheet = getSampleStyleSheet()
        style = sample_style_sheet[style_name]

        for key, value in custom_style.items():
            setattr(style, key, value)

        return style

    def build_pdf(self):
        pdf_buffer = BytesIO()

        try:
            pagesize = PAGE_SIZE
        except NameError:
            pagesize = letter

        try:
            pdf_builder = SimpleDocTemplate(
                pdf_buffer,
                pagesize=pagesize,
                topMargin=BASE_MARGIN,
                leftMargin=BASE_MARGIN,
                rightMargin=BASE_MARGIN,
                bottomMargin=BASE_MARGIN * 2,
            )

            header_style = self.get_style("Heading1")
            meta_style = self.get_style("BodyText", {"fontSize": 11})

            date_metadata = f'Date: {self.date.strftime("%m/%d/%Y")}'
            link_metadata = f'Source URL: <link href="{self.link}">{self.link}</link>'

            raw_flows = [
                Paragraph(self.title, header_style),
                Paragraph(self.author, meta_style) if self.author else None,
                Paragraph(date_metadata, meta_style),
                Paragraph(link_metadata, meta_style),
                Spacer(SPACER["x"], SPACER["y"]),
                *self.build_body(),
            ]

            flows = [item for item in raw_flows if item is not None]

            pdf_builder.multiBuild(
                flows,
                onFirstPage=self.add_page_number,
                onLaterPages=self.add_page_number,
            )

            pdf_value = pdf_buffer.getvalue()
            pdf_buffer.close()

        except Exception as e:
            print(f"Error creating PDF: {e}")
            return None

        return pdf_value
