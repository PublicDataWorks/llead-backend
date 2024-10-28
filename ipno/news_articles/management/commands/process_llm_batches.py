from django.core.management import BaseCommand
from news_articles.services.process_llm_analysis import ProcessLLMAnalysis


class Command(BaseCommand):
    help = "Process completed LLM analysis batches"

    def handle(self, *args, **options):
        processor = ProcessLLMAnalysis()
        
        self.stdout.write("Starting to process completed batches...")
        batches = processor.client.batches.list(limit=100)
        completed_batches = [b for b in batches.data if b.status == "completed" and b.output_file_id]
        
        self.stdout.write(f"Found {len(completed_batches)} completed batches to process")
        processor.process_completed_batches()
        self.stdout.write("Finished processing completed batches")
