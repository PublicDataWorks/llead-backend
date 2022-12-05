from reportlab.lib.units import inch, mm

PAGE_SIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

PAGE_NUMBER = {
    "x": 4.5 * inch,
    "y": 0.4 * inch,
}
SPACER = {
    "x": 0,
    "y": 0.25 * inch,
}
PAGE_NUMBER_FONT = {"TYPE": "Times-Roman", "SIZE": 10.0}

FILE_TYPES = {
    "PDF": "application/pdf",
    "IMG": "image/jpeg",
}

OFFICER_MATCH_THRESHOLD = 0.96

LA_LOC_TOP_LEFT = -94.0693795, 33.0033475
LA_LOC_BOTTOM_RIGHT = -88.707158, 28.892697
MAP_DOT_RADIUS = 8
MAP_DOT_SHARPNESS = 3
