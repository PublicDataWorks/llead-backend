import json
from typing import List
from django.conf import settings
from django.utils import timezone
from pydantic import BaseModel, Field
from openai import OpenAI
from news_articles.models import NewsArticle


class MisconductAnalysis(BaseModel):
    contains_misconduct: bool = Field(description="Indicates if police misconduct is mentioned in the article")
    confidence_score: float = Field(ge=0, le=1, description="Confidence score between 0 and 1")
    explanation: str = Field(description="Brief explanation of the decision")

    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict:
        """Print and return the JSON schema that will be used by OpenAI."""
        schema = super().model_json_schema(*args, **kwargs)
        print("\nGenerated OpenAI Schema:")
        print("------------------------")
        print("type:", schema.get("type"))
        print("properties:", schema.get("properties"))
        print("required:", schema.get("required"))
        print("additionalProperties:", schema.get("additionalProperties", False))
        print("------------------------\n")
        return schema


class ProcessLLMAnalysis:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _create_single_request(self, article: NewsArticle) -> str:
        """Create a JSONL file for a single article batch request."""
        request = {
            "custom_id": str(article.id),
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant analyzing news articles for police misconduct content."},
                    {"role": "user", "content": f"Analyze the following news article text and determine if it contains any reference to police misconduct.\n\nArticle text:\n{article.content}"}
                ],
                "temperature": 0,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": MisconductAnalysis.model_json_schema()
                }
            }
        }

        filename = f"batch_request_{article.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(filename, 'w') as f:
            f.write(json.dumps(request))
        
        return filename

    def _process_batch_results(self, batch_id: str):
        """Process results from a completed batch."""
        batch = self.client.batches.retrieve(batch_id)
        
        if batch.status == "completed" and batch.output_file_id:
            # Download and process results
            output = self.client.files.retrieve_content(batch.output_file_id)
            
            for line in output.splitlines():
                result = json.loads(line)
                article_id = result['custom_id']
                response = result['response']
                
                try:
                    article = NewsArticle.objects.get(id=article_id)
                    
                    if response.get('error'):
                        print(f"Error processing article {article_id}: {response['error']}")
                        article.hide_reason = "LLM processing error"
                        article.save()
                        continue
                    
                    analysis_result = response['body']['choices'][0]['message']['content']
                    article.llm_analysis_result = analysis_result
                    article.is_llm_processed = True
                    
                    # Unhide article if misconduct confidence is above threshold
                    if analysis_result['confidence_score'] >= settings.OPENAI_MISCONDUCT_CONFIDENCE_THRESHOLD:
                        article.is_hidden = False
                    else:
                        article.hide_reason = "Below confidence threshold"
                    
                    article.save()
                    
                except NewsArticle.DoesNotExist:
                    print(f"Article {article_id} not found")
                except Exception as e:
                    print(f"Error processing result for article {article_id}: {str(e)}")

    def _cleanup_file(self, filename: str):
        """Clean up temporary files."""
        import os
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Error cleaning up file {filename}: {str(e)}")

    def submit_unanalyzed_articles(self):
        """Submit each unanalyzed article as a single-item batch."""
        articles = NewsArticle.objects.filter(is_llm_processed=False)
        submitted_batch_ids = []
        
        for article in articles:
            try:
                # Create and upload batch file for single article
                batch_file = self._create_single_request(article)
                file = self.client.files.create(
                    file=open(batch_file, "rb"),
                    purpose="batch"
                )

                # Create batch processing job
                batch = self.client.batches.create(
                    input_file_id=file.id,
                    endpoint="/v1/chat/completions",
                    completion_window="24h"
                )
                
                submitted_batch_ids.append((batch.id, article.id))
                self._cleanup_file(batch_file)
                
            except Exception as e:
                print(f"Error submitting article {article.id}: {str(e)}")
                if 'batch_file' in locals():
                    self._cleanup_file(batch_file)
        
        return submitted_batch_ids

    def process_completed_batches(self):
        """Process results from completed single-item batches."""
        batches = self.client.batches.list(limit=100)
        
        for batch in batches.data:
            if batch.status == "completed" and batch.output_file_id:
                try:
                    output = self.client.files.retrieve_content(batch.output_file_id)
                    result = json.loads(output)  # Single item, no need to iterate
                    
                    article_id = result['custom_id']
                    response = result['response']
                    
                    try:
                        article = NewsArticle.objects.get(id=article_id)
                        
                        if response.get('error'):
                            print(f"Error processing article {article_id}: {response['error']}")
                            article.hide_reason = "LLM processing error"
                            article.save()
                            continue
                        
                        analysis_result = response['body']['choices'][0]['message']['content']
                        article.llm_analysis_result = analysis_result
                        article.is_llm_processed = True
                        
                        # Unhide article if misconduct confidence is above threshold
                        if analysis_result['confidence_score'] >= settings.OPENAI_MISCONDUCT_CONFIDENCE_THRESHOLD:
                            article.is_hidden = False
                        else:
                            article.hide_reason = "Below confidence threshold"
                        
                        article.save()
                        
                    except NewsArticle.DoesNotExist:
                        print(f"Article {article_id} not found")
                    except Exception as e:
                        print(f"Error processing result for article {article_id}: {str(e)}")
                        
                except Exception as e:
                    print(f"Error processing batch {batch.id}: {str(e)}")
