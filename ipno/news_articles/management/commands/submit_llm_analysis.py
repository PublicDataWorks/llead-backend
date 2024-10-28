from django.core.management import BaseCommand
from news_articles.services.process_llm_analysis import ProcessLLMAnalysis


class Command(BaseCommand):
    help = "Submit unprocessed news articles for batch LLM analysis"

    def handle(self, *args, **options):
        processor = ProcessLLMAnalysis()
        submitted_batches = processor.submit_unanalyzed_articles()
        self.stdout.write(f"Submitted {len(submitted_batches)} articles for processing")
        for batch_id, article_id in submitted_batches:
            self.stdout.write(f"Article {article_id} submitted as batch {batch_id}")
