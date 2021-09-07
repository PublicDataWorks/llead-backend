from reportlab.lib.units import mm, inch

PAGE_SIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

PAGE_NUMBER = {
    'x': 4.5 * inch,
    'y': 0.4 * inch,
}
SPACER = {
    'x': 0,
    'y': 0.25 * inch,
}
PAGE_NUMBER_FONT = {
    "TYPE": 'Times-Roman',
    "SIZE": 10.
}

FILE_TYPES = {
    'PDF': 'application/pdf',
    'IMG': 'image/jpeg',
}

OFFICER_MATCH_THRESHOLD = 0.96
