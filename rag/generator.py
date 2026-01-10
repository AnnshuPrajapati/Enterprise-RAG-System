"""
Local LLM generator for RAG system using GPT4All.
Provides answer generation based on retrieved document chunks.
"""

import os
import time
from typing import List, Dict, Any, Optional
from gpt4all import GPT4All
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLMGenerator:
    """
    Local LLM generator using GPT4All for answer generation.
    Downloads and manages local LLM models for offline inference.
    """

    def __init__(self, model_name: str = "orca-mini-3b-gguf2-q4_0.gguf", model_path: str = None):
        """
        Initialize the local LLM generator.

        Args:
            model_name: Name of the GPT4All model to use
            model_path: Custom path for model storage (optional)
        """
        self.model_name = model_name
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_path, exist_ok=True)

        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the GPT4All model."""
        try:
            logger.info(f"Loading GPT4All model: {self.model_name}")
            self.model = GPT4All(self.model_name, model_path=self.model_path)

            # Warm up the model
            logger.info("Warming up the model...")
            self.model.generate("Hello", max_tokens=10, temp=0.1)
            logger.info("Model loaded and ready!")

        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            # Fallback to a smaller model if available
            try:
                logger.info("Trying fallback model...")
                self.model_name = "ggml-model-gpt4all-falcon-q4_0.bin"
                self.model = GPT4All(self.model_name, model_path=self.model_path)
                self.model.generate("Hello", max_tokens=10, temp=0.1)
                logger.info("Fallback model loaded successfully!")
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                raise RuntimeError("Could not load any GPT4All model. Please check your installation.")

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]],
                       max_tokens: int = 256, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate an answer based on the query and retrieved context chunks.

        Args:
            query: User's question
            context_chunks: List of retrieved document chunks with metadata
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Dictionary containing answer, sources, and metadata
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Cannot generate answers.")

        # Extract relevant information from chunks
        context_texts = []
        source_documents = set()

        for chunk in context_chunks:
            context_texts.append(chunk['text'])
            metadata = chunk.get('metadata', {})
            doc_name = metadata.get('document_name', 'Unknown')
            source_documents.add(doc_name)

        # Combine context into a single string
        context = "\n\n".join(context_texts)
        sources = sorted(list(source_documents))

        # Create the prompt
        prompt = self._create_rag_prompt(query, context)

        try:
            logger.info(f"Generating answer for query: {query[:50]}...")

            # Generate response
            start_time = time.time()
            response = self.model.generate(
                prompt,
                max_tokens=max_tokens,
                temp=temperature,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
            generation_time = time.time() - start_time

            # Clean up the response
            answer = self._clean_response(response)

            result = {
                "answer": answer,
                "sources": sources,
                "context_chunks_used": len(context_chunks),
                "generation_time_seconds": round(generation_time, 2),
                "model": self.model_name,
                "query": query
            }

            logger.info(f"Generated answer in {generation_time:.2f}s using {len(context_chunks)} chunks")
            return result

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I apologize, but I encountered an error while generating an answer. Please try again.",
                "sources": sources,
                "error": str(e),
                "context_chunks_used": len(context_chunks),
                "query": query
            }

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create a RAG-style prompt for the LLM."""
        prompt = f"""You are a helpful AI assistant that answers questions based on provided document context.

CONTEXT:
{context}

QUESTION: {query}

INSTRUCTIONS:
- Answer the question using ONLY the information from the provided context
- Be concise but comprehensive
- If the context doesn't contain enough information to answer fully, say so
- Cite specific document names when relevant
- Keep your answer focused and relevant

ANSWER:"""

        return prompt

    def _clean_response(self, response: str) -> str:
        """Clean up the LLM response."""
        # Remove any prompt leakage
        if "ANSWER:" in response:
            response = response.split("ANSWER:", 1)[1].strip()

        # Remove excessive whitespace
        response = response.strip()

        # Limit to reasonable length (first coherent response)
        if len(response) > 2000:
            # Try to cut at a sentence boundary
            sentences = response.split('.')
            truncated = []
            length = 0
            for sentence in sentences:
                if length + len(sentence) > 1500:
                    break
                truncated.append(sentence + '.')
                length += len(sentence)

            if truncated:
                response = ' '.join(truncated)

        return response

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "status": "loaded" if self.model else "not_loaded"
        }


# Global generator instance for reuse
_generator_instance = None

def get_generator() -> LocalLLMGenerator:
    """Get or create the global generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LocalLLMGenerator()
    return _generator_instance
