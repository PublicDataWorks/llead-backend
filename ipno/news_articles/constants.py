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
BRPROUD_SOURCE = 'brproud'
BOSSIERPRESS_SOURCE = 'bossierpress'
HERALDGUIDE_SOURCE = 'heraldguide'
PRESSHERALD_SOURCE = 'pressherald'
ULMHAWKEYEONLINE_SOURCE = 'ulmhawkeyeonline'
MYARKLAMISS_SOURCE = 'myarklamiss'
NATCHITOCHESTIMES_SOURCE = 'natchitochestimes'
IBERIANET_SOURCE = 'iberianet'
BIZNEWORLEANS_SOURCE = 'bizneworleans'
JAMBALAYANEWS_SOURCE = 'jambalayanews'
LOUISIANAWEEKLY_SOURCE = 'louisianaweekly'
LOYOLAMAROON_SOURCE = 'loyolamaroon'
WGNO_SOURCE = 'wgno'
UPTOWNMESSENGER_SOURCE = 'uptownmessenger'
RUSTONLEADER_SOURCE = 'rustonleader'
SLIDELLINDEPENDENT_SOURCE = 'slidellindependent'
TECHETODAY_SOURCE = 'techetoday'
THENICHOLLSWORTH_SOURCE = 'thenichollsworth'
THEACADIANAADVOCATE_SOURCE = 'theacadianaadvocate'
LSUREVEILLE_SOURCE = 'lsureveille'
CONCORDIASENTINELHANNAPUB_SOURCE = 'concordiasentinelhannapub'
FRANKLINSUNHANNAPUB_SOURCE = 'franklinsunhannapub'
OUACHITACITIZENHANNAPUB_SOURCE = 'ouachitacitizenhannapub'
WBRZ_SOURCE = 'wbrz'
THETOWNTALK_SOURCE = 'thetowntalk'
SHREVEPORTTIMES_SOURCE = 'shreveporttimes'

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
    {
        'source_name': BRPROUD_SOURCE,
        'custom_matching_name': 'BR Proud',
    },
    {
        'source_name': BOSSIERPRESS_SOURCE,
        'custom_matching_name': 'Bossier Press-Tribune',
    },
    {
        'source_name': HERALDGUIDE_SOURCE,
        'custom_matching_name': 'Herald Guide'
    },
    {
        'source_name': PRESSHERALD_SOURCE,
        'custom_matching_name': 'Minden Press-Herald'
    },
    {
        'source_name': ULMHAWKEYEONLINE_SOURCE,
        'custom_matching_name': 'The Hawkeye'
    },
    {
        'source_name': MYARKLAMISS_SOURCE,
        'custom_matching_name': 'My ArkLAMISS'
    },
    {
        'source_name': NATCHITOCHESTIMES_SOURCE,
        'custom_matching_name': 'Natchioches Times'
    },
    {
        'source_name': IBERIANET_SOURCE,
        'custom_matching_name': 'The Daily Iberian'
    },
    {
        'source_name': BIZNEWORLEANS_SOURCE,
        'custom_matching_name': 'Biz New Orleans'
    },
    {
        'source_name': JAMBALAYANEWS_SOURCE,
        'custom_matching_name': 'Jambalaya News'
    },
    {
        'source_name': LOUISIANAWEEKLY_SOURCE,
        'custom_matching_name': 'The Louisiana Weekly'
    },
    {
        'source_name': LOYOLAMAROON_SOURCE,
        'custom_matching_name': 'The Maroon'
    },
    {
        'source_name': WGNO_SOURCE,
        'custom_matching_name': 'WGNO'
    },
    {
        'source_name': UPTOWNMESSENGER_SOURCE,
        'custom_matching_name': 'Uptown Messenger'
    },
    {
        'source_name': RUSTONLEADER_SOURCE,
        'custom_matching_name': 'Ruston Daily Leader'
    },
    {
        'source_name': SLIDELLINDEPENDENT_SOURCE,
        'custom_matching_name': 'Slidell Independent'
    },
    {
        'source_name': TECHETODAY_SOURCE,
        'custom_matching_name': 'Teche Today'
    },
    {
        'source_name': THENICHOLLSWORTH_SOURCE,
        'custom_matching_name': 'Nicholls Worth'
    },
    {
        'source_name': THEACADIANAADVOCATE_SOURCE,
        'custom_matching_name': 'The Acadiana Advocate'
    },
    {
        'source_name': LSUREVEILLE_SOURCE,
        'custom_matching_name': 'Reveille'
    },
    {
        'source_name': CONCORDIASENTINELHANNAPUB_SOURCE,
        'custom_matching_name': 'Concordia Sentinel'
    },
    {
        'source_name': FRANKLINSUNHANNAPUB_SOURCE,
        'custom_matching_name': 'The Franklin Sun'
    },
    {
        'source_name': OUACHITACITIZENHANNAPUB_SOURCE,
        'custom_matching_name': 'The Oouachita Citizen'
    },
    {
        'source_name': WBRZ_SOURCE,
        'custom_matching_name': 'WBRZ'
    },
    {
        'source_name': THETOWNTALK_SOURCE,
        'custom_matching_name': 'Town Talk'
    },
    {
        'source_name': SHREVEPORTTIMES_SOURCE,
        'custom_matching_name': 'Shreveport Times'
    },
]

NEWS_ARTICLES_LIMIT = 20

NEWS_ARTICLE_OFFICER_WRGL_COLUMNS = ['uid', 'officer_id', 'newsarticle_id', 'id']
