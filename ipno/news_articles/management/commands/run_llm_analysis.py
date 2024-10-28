from django.core.management import BaseCommand

from news_articles.services.process_llm_analysis import ProcessLLMAnalysis


class Command(BaseCommand):
    help = "Process unanalyzed news articles with OpenAI LLM to detect police misconduct content"

    def handle(self, *args, **options):
        processor = ProcessLLMAnalysis()
        processor.process_unanalyzed_articles()
