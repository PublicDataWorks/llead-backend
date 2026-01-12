import unittest
from unittest.mock import patch, MagicMock
from news_articles.services.openai_llm_service import OpenAILLMService

class TestOpenAILLMService(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.service = OpenAILLMService(api_key=self.api_key)

    @patch("news_articles.services.openai_llm_service.openai.Completion.create")
    def test_get_confidence_score(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices[0].text.strip.return_value = "0.85"
        mock_create.return_value = mock_response

        article_text = "This is a test article text."
        score = self.service.get_confidence_score(article_text)

        self.assertEqual(score, 0.85)
        mock_create.assert_called_once_with(
            engine="gpt-4",
            prompt="Does the text of this article contain any reference to police misconduct? This is a test article text.",
            max_tokens=1,
            n=1,
            stop=None,
            temperature=0.5,
        )

    @patch("news_articles.services.openai_llm_service.openai.Completion.create")
    def test_get_confidence_score_error_handling(self, mock_create):
        mock_create.side_effect = Exception("API error")

        article_text = "This is a test article text."
        score = self.service.get_confidence_score(article_text)

        self.assertIsNone(score)
