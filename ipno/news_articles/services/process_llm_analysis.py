from django.conf import settings
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

    def analyze_article(self, article):
        try:
            # Print schema before making the API call
            MisconductAnalysis.model_json_schema()
            
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant analyzing news articles for police misconduct content."},
                    {"role": "user", "content": f"Analyze the following news article text and determine if it contains any reference to police misconduct.\n\nArticle text:\n{article.content}"}
                ],
                temperature=0,
                response_format=MisconductAnalysis
            )
            
            if completion.choices[0].message.refusal:
                print(f"Article {article.id} analysis was refused: {completion.choices[0].message.refusal}")
                return None

            result = completion.choices[0].message.parsed
            article.llm_analysis_result = result.model_dump()
            article.is_llm_processed = True
            article.save()
            
            return result.model_dump()
        except Exception as e:
            print(f"Error analyzing article {article.id}: {str(e)}")
            return None

    def process_unanalyzed_articles(self):
        articles = NewsArticle.objects.filter(is_llm_processed=False)
        
        for article in articles:
            self.analyze_article(article)
