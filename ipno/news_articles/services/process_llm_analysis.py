from django.conf import settings
import openai
from news_articles.models import NewsArticle

MISCONDUCT_PROMPT = """
Analyze the following news article text and determine if it contains any reference to police misconduct.
Respond with a JSON object containing:
1. "contains_misconduct": boolean indicating if misconduct is mentioned
2. "confidence_score": float between 0 and 1 indicating confidence in the assessment
3. "explanation": brief explanation of the decision

Article text:
{text}
"""

class ProcessLLMAnalysis:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def analyze_article(self, article):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant analyzing news articles for police misconduct content."},
                    {"role": "user", "content": MISCONDUCT_PROMPT.format(text=article.content)}
                ],
                temperature=0,
                response_format={ "type": "json" }
            )
            
            result = response.choices[0].message.content
            
            article.llm_analysis_result = result
            article.is_llm_processed = True
            article.save()
            
            return result
        except Exception as e:
            print(f"Error analyzing article {article.id}: {str(e)}")
            return None

    def process_unanalyzed_articles(self):
        articles = NewsArticle.objects.filter(is_llm_processed=False)
        
        for article in articles:
            self.analyze_article(article)
