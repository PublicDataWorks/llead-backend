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

NEWS_ARTICLE_WRGL_COLUMNS = [
    'id', 'source_name', 'guid', 'link', 'url',
    'published_date', 'author', 'title', 'content',
]

CRAWL_STATUS_OPENED = 'started'
CRAWL_STATUS_FINISHED = 'finished'
CRAWL_STATUS_ERROR = 'error'

CRAWL_STATUSES = (
    (CRAWL_STATUS_OPENED, 'Started'),
    (CRAWL_STATUS_FINISHED, 'Finished'),
    (CRAWL_STATUS_ERROR, 'Error')
)

NOLA_SOURCE = 'nola'
THELENSNOLA_SOURCE = 'thelensnola'
VERMILIONTODAY_SOURCE = 'vermiliontoday'
KLAX_SOURCE = 'klax'
TTFMAGAZINE_SOURCE = 'ttfmagazine'
CAPITALCITYNEWS_SOURCE = 'capitalcitynews'

APP_NEWS_ARTICLE_NAMES = [
    {
        'source_name': THELENSNOLA_SOURCE,
        'custom_matching_name': 'The Lens NOLA',
    },
    {
        'source_name': NOLA_SOURCE,
        'custom_matching_name': 'The Advocate',
    },
    {
        'source_name': VERMILIONTODAY_SOURCE,
        'custom_matching_name': 'Vermillion Today',
    },
    {
        'source_name': KLAX_SOURCE,
        'custom_matching_name': 'KLAX',
    },
    {
        'source_name': TTFMAGAZINE_SOURCE,
        'custom_matching_name': '225 Magazine',
    },
    {
        'source_name': CAPITALCITYNEWS_SOURCE,
        'custom_matching_name': 'Capital City News',
    },
]

NEWS_ARTICLES_LIMIT = 20

NEWS_ARTICLE_OFFICER_WRGL_COLUMNS = ['uid', 'officer_id', 'newsarticle_id', 'id']
