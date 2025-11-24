from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import json
from .models import Conference, Question


class ConferenceViewsTests(TestCase):
    def setUp(self):
        self.conference = Conference.objects.create(name="Existing Conference")
        self.create_url = reverse("conference_create")
        self.update_url = reverse("conference_update", args=[self.conference.id])
        self.delete_url = reverse("conference_delete", args=[self.conference.id])
        self.index_url = reverse("index")

    # -----------------------------
    # ConferenceCreateView
    # -----------------------------
    def test_conference_create_get(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_form.html")
        self.assertIn("conference_form", response.context)
        self.assertIn("formset", response.context)

    def test_conference_create_post_valid_with_questions(self):
        """POST valid conference + valid question formset creates both."""
        data = {
            "name": "Conference With Questions",
            "question_set-TOTAL_FORMS": "1",
            "question_set-INITIAL_FORMS": "0",
            "question_set-MIN_NUM_FORMS": "1",
            "question_set-MAX_NUM_FORMS": "1000",
            "question_set-0-id":"",
            "question_set-0-conference": "",
            "question_set-0-question_text": "What is AI?",
            "question_set-0-position": "0",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)

        conference = Conference.objects.get(name="Conference With Questions")
        questions = Question.objects.filter(conference=conference)
        self.assertEqual(questions.count(), 1)
        self.assertEqual(questions.first().question_text, "What is AI?")

    def test_conference_create_post_invalid_no_questions(self):
        """POST conference without questions should fail due to min_num=1."""
        data = {
            "name": "Conference With Questions",
            "question_set-TOTAL_FORMS": "0",
            "question_set-INITIAL_FORMS": "0",
            "question_set-MIN_NUM_FORMS": "1",
            "question_set-MAX_NUM_FORMS": "1000"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_form.html")

        errors = response.context["formset"].non_form_errors()
        self.assertIn(" Please submit at least 1 question.", errors)
        self.assertFalse(Conference.objects.filter(name="Invalid Conference").exists())

    def test_conference_create_post_invalid_conference_form(self):
        """POST invalid conference name should re-render form with errors."""
        data = {
            "name": "",
            "question_set-TOTAL_FORMS": "1",
            "question_set-INITIAL_FORMS": "0",
            "question_set-MIN_NUM_FORMS": "1",
            "question_set-MAX_NUM_FORMS": "1000",
            "question_set-0-id":"",
            "question_set-0-conference": "",
            "question_set-0-question_text": "What is AI?",
            "question_set-0-position": "0",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_form.html")
        self.assertFormError(response.context["conference_form"], "name", "This field is required.")
        self.assertFalse(Conference.objects.exclude(name="Existing Conference").exists())

    # -----------------------------
    # ConferenceUpdateView
    # -----------------------------
    def test_conference_update_get(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_form.html")
        self.assertTrue(response.context["is_edit"])
        self.assertEqual(response.context["conference"].id, self.conference.id)

    def test_conference_update_post_valid(self):
        """POST valid data should update name and replace questions."""
        data = {
            "name": "Updated Conference",
            "question_set-TOTAL_FORMS": "1",
            "question_set-INITIAL_FORMS": "0",
            "question_set-MIN_NUM_FORMS": "1",
            "question_set-MAX_NUM_FORMS": "1000",
            "question_set-0-id":"",
            "question_set-0-conference": "",
            "question_set-0-question_text": "Updated Question?",
            "question_set-0-position": "0",
        }
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)
        self.conference.refresh_from_db()
        self.assertEqual(self.conference.name, "Updated Conference")
        self.assertEqual(Question.objects.filter(conference=self.conference).count(), 1)

    def test_conference_update_post_invalid_no_questions(self):
        """POST update with no questions should fail validation."""
        data = {
            "name": "No Questions Conference",
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_form.html")
        errors = response.context["formset"].non_form_errors()
        self.assertIn(" Please submit at least 1 question.", errors)
        self.conference.refresh_from_db()
        self.assertEqual(self.conference.name, "Existing Conference")

    # -----------------------------
    # conference_delete view
    # -----------------------------
    def test_conference_delete_get(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/conference/conference_confirm_delete.html")
        self.assertEqual(response.context["conference"], self.conference)

    def test_conference_delete_post(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.index_url)
        self.assertFalse(Conference.objects.filter(pk=self.conference.pk).exists())


class IndexViewTests(TestCase):
    def setUp(self):
        """Set up test conference with questions for paper upload tests."""
        self.conference = Conference.objects.create(name="Test Conference")
        Question.objects.create(
            conference=self.conference,
            question_text="Is the methodology sound?",
            position=1
        )
        Question.objects.create(
            conference=self.conference,
            question_text="Are results clearly presented?",
            position=2
        )
        self.index_url = reverse("index")
        
        # Create a simple PDF mock file
        self.pdf_content = b"%PDF-1.4\n%Mock PDF content"
        self.pdf_file = SimpleUploadedFile(
            "test_paper.pdf",
            self.pdf_content,
            content_type="application/pdf"
        )

    # -----------------------------
    # IndexView GET
    # -----------------------------
    def test_index_view_get(self):
        """GET request should render form."""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/index.html")
        self.assertIn("form", response.context)
        self.assertIsNotNone(response.context["form"])

    # -----------------------------
    # IndexView POST - Valid
    # -----------------------------
    @patch('app.paper_grader.views.index_views.ollama.Client')
    @patch('app.paper_grader.views.index_views.pymupdf.open')
    @patch('app.paper_grader.views.index_views.pymupdf4llm.to_markdown')
    def test_index_view_post_valid_with_api_key(self, mock_to_markdown, mock_pymupdf_open, mock_ollama_client):
        """POST with valid form and API key should process paper and return results."""
        # Mock PDF processing
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        mock_to_markdown.return_value = "# Test Paper\n\nThis is a test paper content."
        
        # Mock LLM response
        mock_client_instance = MagicMock()
        mock_ollama_client.return_value = mock_client_instance
        
        mock_message = MagicMock()
        mock_message.content = json.dumps([
            {
                "position": 1,
                "question": "Is the methodology sound?",
                "rating": "yes",
                "explanation": "The methodology is well-designed and rigorous."
            },
            {
                "position": 2,
                "question": "Are results clearly presented?",
                "rating": "partial",
                "explanation": "Results are presented but could be clearer."
            }
        ])
        
        mock_chat_response = MagicMock()
        mock_chat_response.message = mock_message
        mock_client_instance.chat.return_value = mock_chat_response
        
        # Prepare form data
        data = {
            'conference': self.conference.id,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'ollama_api_key': 'test-api-key'
        }
        
        response = self.client.post(
            self.index_url,
            data=data,
            files={'files': self.pdf_file}
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/results.html")
        self.assertIn("ratings", response.context)
        self.assertIn("conference", response.context)
        self.assertEqual(len(response.context["ratings"]), 2)
        self.assertEqual(response.context["conference"], self.conference)
        
        # Verify ollama.Client was called with API key
        mock_ollama_client.assert_called_once_with(
            host='http://localhost:11434',
            headers={'Authorization': 'Bearer test-api-key'}
        )
        
        # Verify PDF was processed
        mock_pymupdf_open.assert_called_once()
        mock_to_markdown.assert_called_once_with(mock_doc)
        mock_doc.close.assert_called_once()

    @patch('app.paper_grader.views.index_views.ollama.Client')
    @patch('app.paper_grader.views.index_views.pymupdf.open')
    @patch('app.paper_grader.views.index_views.pymupdf4llm.to_markdown')
    def test_index_view_post_valid_without_api_key(self, mock_to_markdown, mock_pymupdf_open, mock_ollama_client):
        """POST without API key should use ollama.Client without headers."""
        # Mock PDF processing
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        mock_to_markdown.return_value = "# Test Paper"
        
        # Mock LLM response
        mock_client_instance = MagicMock()
        mock_ollama_client.return_value = mock_client_instance
        
        mock_message = MagicMock()
        mock_message.content = json.dumps([
            {
                "position": 1,
                "question": "Is the methodology sound?",
                "rating": "yes",
                "explanation": "Good methodology."
            }
        ])
        
        mock_chat_response = MagicMock()
        mock_chat_response.message = mock_message
        mock_client_instance.chat.return_value = mock_chat_response
        
        # Prepare form data without API key
        data = {
            'conference': self.conference.id,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'ollama_api_key': ''  # Empty API key
        }
        
        response = self.client.post(
            self.index_url,
            data=data,
            files={'files': self.pdf_file}
        )
        
        # Verify ollama.Client was called without headers
        mock_ollama_client.assert_called_once_with(host='http://localhost:11434')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/results.html")

    @patch('app.paper_grader.views.index_views.ollama.Client')
    @patch('app.paper_grader.views.index_views.pymupdf.open')
    @patch('app.paper_grader.views.index_views.pymupdf4llm.to_markdown')
    def test_index_view_post_ratings_sorted_by_position(self, mock_to_markdown, mock_pymupdf_open, mock_ollama_client):
        """Ratings should be sorted by position even if returned out of order."""
        # Mock PDF processing
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        mock_to_markdown.return_value = "# Test Paper"
        
        # Mock LLM response with unsorted data
        mock_client_instance = MagicMock()
        mock_ollama_client.return_value = mock_client_instance
        
        mock_message = MagicMock()
        # Return ratings out of order
        mock_message.content = json.dumps([
            {
                "position": 2,
                "question": "Second question",
                "rating": "yes",
                "explanation": "Second answer"
            },
            {
                "position": 1,
                "question": "First question",
                "rating": "no",
                "explanation": "First answer"
            }
        ])
        
        mock_chat_response = MagicMock()
        mock_chat_response.message = mock_message
        mock_client_instance.chat.return_value = mock_chat_response
        
        data = {
            'conference': self.conference.id,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'ollama_api_key': ''
        }
        
        response = self.client.post(
            self.index_url,
            data=data,
            files={'files': self.pdf_file}
        )
        
        # Verify ratings are sorted by position
        ratings = response.context["ratings"]
        self.assertEqual(ratings[0]["position"], 1)
        self.assertEqual(ratings[1]["position"], 2)

    # -----------------------------
    # IndexView POST - Invalid
    # -----------------------------
    def test_index_view_post_invalid_form(self):
        """POST with invalid form should re-render form with errors."""
        # Missing required fields
        data = {
            'conference': '',
            'ollama_url': '',
            'ollama_model': '',
        }
        
        response = self.client.post(self.index_url, data=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/index.html")
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())

    @patch('app.paper_grader.views.index_views.ollama.Client')
    @patch('app.paper_grader.views.index_views.pymupdf.open')
    @patch('app.paper_grader.views.index_views.pymupdf4llm.to_markdown')
    def test_index_view_post_json_decode_error(self, mock_to_markdown, mock_pymupdf_open, mock_ollama_client):
        """POST with invalid JSON response from LLM should show error."""
        # Mock PDF processing
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        mock_to_markdown.return_value = "# Test Paper"
        
        # Mock LLM response with invalid JSON
        mock_client_instance = MagicMock()
        mock_ollama_client.return_value = mock_client_instance
        
        mock_message = MagicMock()
        mock_message.content = "This is not valid JSON {invalid}"
        
        mock_chat_response = MagicMock()
        mock_chat_response.message = mock_message
        mock_client_instance.chat.return_value = mock_chat_response
        
        data = {
            'conference': self.conference.id,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'ollama_api_key': ''
        }
        
        response = self.client.post(
            self.index_url,
            data=data,
            files={'files': self.pdf_file}
        )
        
        # Verify error handling
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paper_grader/results.html")
        self.assertIn("error", response.context)
        self.assertIn("Failed to parse LLM response", response.context["error"])
        self.assertIn("raw_text", response.context)
        self.assertEqual(response.context["ratings"], [])
        self.assertEqual(response.context["raw_text"], "This is not valid JSON {invalid}")

    @patch('app.paper_grader.views.index_views.ollama.Client')
    @patch('app.paper_grader.views.index_views.pymupdf.open')
    @patch('app.paper_grader.views.index_views.pymupdf4llm.to_markdown')
    def test_index_view_llm_processing_message_format(self, mock_to_markdown, mock_pymupdf_open, mock_ollama_client):
        """Verify the message sent to LLM contains correct format."""
        # Mock PDF processing
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        mock_to_markdown.return_value = "# Test Paper Content"
        
        # Mock LLM
        mock_client_instance = MagicMock()
        mock_ollama_client.return_value = mock_client_instance
        
        mock_message = MagicMock()
        mock_message.content = json.dumps([{"position": 1, "question": "Q1", "rating": "yes", "explanation": "E1"}])
        
        mock_chat_response = MagicMock()
        mock_chat_response.message = mock_message
        mock_client_instance.chat.return_value = mock_chat_response
        
        data = {
            'conference': self.conference.id,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'ollama_api_key': ''
        }
        
        self.client.post(
            self.index_url,
            data=data,
            files={'files': self.pdf_file}
        )
        
        # Verify chat was called with correct structure
        mock_client_instance.chat.assert_called_once()
        call_kwargs = mock_client_instance.chat.call_args[1]
        
        self.assertEqual(call_kwargs['model'], 'llama2')
        self.assertIn('messages', call_kwargs)
        self.assertEqual(len(call_kwargs['messages']), 1)
        self.assertEqual(call_kwargs['messages'][0]['role'], 'user')
        
        # Verify message content includes conference name and questions
        message_content = call_kwargs['messages'][0]['content']
        self.assertIn('Test Conference', message_content)
        self.assertIn('Is the methodology sound?', message_content)
        self.assertIn('Are results clearly presented?', message_content)
        self.assertIn('# Test Paper Content', message_content)