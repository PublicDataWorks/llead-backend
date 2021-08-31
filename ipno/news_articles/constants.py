NEWS_ARTICLE_CLOUD_SPACES = 'news_articles'
TAG_STYLE_MAPPINGS = {
    'h1': 'Heading1',
    'h2': 'Heading2',
    'h3': 'Heading3',
    'h4': 'Heading4',
    'h5': 'Heading5',
    'p': 'BodyText',
}

UNPARSED_TAGS = [
    'aside',
    'nav'
]

ARTICLE_MATCHING_KEYWORDS = [
    'police',
    'officer',
    'NOPD',
    'LSP'
]


NEWS_ARTICLE_WRGL_COLUMNS = [
    'id', 'source_name', 'guid', 'link', 'url', 'preview_image_url',
    'published_date', 'author', 'title', 'content',
]

NEWS_ARTICLE_OFFICER_WRGL_COLUMNS = ['uid', 'officer_id', 'newsarticle_id', 'id']

BASE_CRAWLER_LIMIT = 100
