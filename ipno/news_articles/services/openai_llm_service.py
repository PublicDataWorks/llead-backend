import openai
import logging

class OpenAILLMService:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def get_confidence_score(self, article_text):
        try:
            response = openai.Completion.create(
                engine="gpt-4",
                prompt=f"Does the text of this article contain any reference to police misconduct? {article_text}",
                max_tokens=1,
                n=1,
                stop=None,
                temperature=0.5,
            )
            score = response.choices[0].text.strip()
            return float(score)
        except Exception as e:
            logging.error(f"Error while calling OpenAI API: {e}")
            return None
