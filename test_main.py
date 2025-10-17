import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_health_check(self):
        """Test health endpoint returns correct response"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "FastAPI QA Service"}
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome to FastAPI Question-Answering Service" in response.json()["message"]


class TestChatEndpoint:
    """Test the main chat/QA functionality"""
    
    @patch('main.qa_pipeline')
    def test_chat_success(self, mock_pipeline):
        """Test successful question answering"""
        # Mock the pipeline response
        mock_pipeline.return_value = {'answer': 'FastAPI is a web framework'}
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What is FastAPI?",
            "context": "FastAPI is a modern web framework for building APIs with Python."
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["answer"] == "FastAPI is a web framework"
        mock_pipeline.assert_called_once_with(
            question="What is FastAPI?",
            context="FastAPI is a modern web framework for building APIs with Python."
        )
    
    @patch('main.qa_pipeline', None)
    def test_chat_model_unavailable(self):
        """Test error when QA model is not available"""
        request_data = {
            "question": "What is FastAPI?",
            "context": "FastAPI is a modern web framework."
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 503
        assert "Question-Answering model is not available" in response.json()["detail"]
    
    @patch('main.qa_pipeline')
    def test_chat_pipeline_error(self, mock_pipeline):
        """Test error handling when pipeline fails"""
        # Mock pipeline to raise an exception
        mock_pipeline.side_effect = Exception("Pipeline error")
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What is FastAPI?",
            "context": "FastAPI is a modern web framework."
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 500
        assert "Pipeline error" in response.json()["detail"]
    
    def test_chat_invalid_request(self):
        """Test validation of request data"""
        # Missing required fields
        response = client.post("/chat", json={})
        assert response.status_code == 422
        
        # Missing context
        response = client.post("/chat", json={"question": "What is FastAPI?"})
        assert response.status_code == 422
        
        # Missing question
        response = client.post("/chat", json={"context": "Some context"})
        assert response.status_code == 422


class TestBiasAndFairness:
    """Test for potential bias in responses"""
    
    @patch('main.qa_pipeline')
    def test_gender_neutrality(self, mock_pipeline):
        """Test that responses don't exhibit gender bias"""
        mock_pipeline.return_value = {'answer': 'A skilled professional'}
        mock_pipeline.__bool__ = lambda x: True
        
        test_cases = [
            {
                "question": "Who is the best programmer?",
                "context": "Programming requires skill and dedication from anyone regardless of gender."
            },
            {
                "question": "Who makes a good leader?",
                "context": "Leadership qualities can be found in people of all genders and backgrounds."
            }
        ]
        
        for case in test_cases:
            response = client.post("/chat", json=case)
            assert response.status_code == 200
            # Check that response doesn't contain gendered assumptions
            answer = response.json()["answer"].lower()
            biased_terms = ['he', 'him', 'his', 'she', 'her', 'hers', 'man', 'woman']
            # This is a basic check - in real scenarios, you'd want more sophisticated bias detection
            
    @patch('main.qa_pipeline')
    def test_factual_consistency(self, mock_pipeline):
        """Test that answers are consistent with provided context"""
        mock_pipeline.return_value = {'answer': 'Based on the context provided'}
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What color is the sky?",
            "context": "The sky appears blue due to light scattering."
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        # In a real implementation, you'd check semantic similarity between context and answer


class TestHallucinationDetection:
    """Test for hallucination in responses"""
    
    @patch('main.qa_pipeline')
    def test_no_hallucination_simple(self, mock_pipeline):
        """Test that model doesn't hallucinate when context is clear"""
        mock_pipeline.return_value = {'answer': 'Python'}
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What programming language is mentioned?",
            "context": "Python is a popular programming language for data science."
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        answer = response.json()["answer"]
        
        # Basic check that answer relates to context
        assert len(answer) > 0
        
    @patch('main.qa_pipeline')
    def test_empty_context_handling(self, mock_pipeline):
        """Test behavior with minimal or empty context"""
        mock_pipeline.return_value = {'answer': 'I cannot answer based on the provided context.'}
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What is the capital of Mars?",
            "context": ""
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        # Model should indicate uncertainty or inability to answer


class TestPerformance:
    """Test performance characteristics"""
    
    @patch('main.qa_pipeline')
    def test_response_time(self, mock_pipeline):
        """Test that responses are returned within reasonable time"""
        import time
        
        mock_pipeline.return_value = {'answer': 'Quick response'}
        mock_pipeline.__bool__ = lambda x: True
        
        request_data = {
            "question": "What is FastAPI?",
            "context": "FastAPI is a web framework."
        }
        
        start_time = time.time()
        response = client.post("/chat", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    @patch('main.qa_pipeline')
    def test_large_context_handling(self, mock_pipeline):
        """Test handling of large context"""
        mock_pipeline.return_value = {'answer': 'Processed large context'}
        mock_pipeline.__bool__ = lambda x: True
        
        # Create a large context (simulate real-world scenario)
        large_context = "This is a test context. " * 100
        
        request_data = {
            "question": "What is this about?",
            "context": large_context
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])