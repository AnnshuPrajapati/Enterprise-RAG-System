"""
Document chunking utilities for the RAG system.
Provides functions to split text documents into manageable chunks with metadata.
"""

from typing import List, Dict, Any
import re


class DocumentChunker:
    """Handles document text chunking with metadata preservation."""

    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        """
        Initialize the document chunker.

        Args:
            chunk_size: Target number of words per chunk
            chunk_overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Args:
            text: The full text to chunk
            metadata: Base metadata to include with each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean and normalize text
        text = self._clean_text(text)

        # Split into sentences for better chunking
        sentences = self._split_into_sentences(text)

        # Create chunks
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 1

        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_word_count = len(sentence_words)

            # If adding this sentence would exceed chunk size and we have content
            if current_word_count + sentence_word_count > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk_text = ' '.join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_id': chunk_id,
                    'word_count': current_word_count,
                    'section': f"chunk_{chunk_id:03d}"
                })

                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata
                })

                # Start new chunk with overlap
                overlap_words = self._get_overlap_words(current_chunk, self.chunk_overlap)
                current_chunk = overlap_words + sentence_words
                current_word_count = len(current_chunk)
                chunk_id += 1
            else:
                # Add sentence to current chunk
                current_chunk.extend(sentence_words)
                current_word_count += sentence_word_count

        # Add final chunk if there's remaining content
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': chunk_id,
                'word_count': current_word_count,
                'section': f"chunk_{chunk_id:03d}"
            })

            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })

        # Update total_chunks in all chunks
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be enhanced with NLTK if needed
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _get_overlap_words(self, words: List[str], overlap_count: int) -> List[str]:
        """Get the last N words for overlap."""
        return words[-overlap_count:] if len(words) >= overlap_count else words


def chunk_document(text: str, document_name: str, source_file: str,
                  chunk_size: int = 200) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk a document with standard metadata.

    Args:
        text: Document text
        document_name: Name of the document
        source_file: Source filename
        chunk_size: Words per chunk

    Returns:
        List of chunk dictionaries
    """
    chunker = DocumentChunker(chunk_size=chunk_size)

    metadata = {
        'document_name': document_name,
        'source_file': source_file
    }

    return chunker.chunk_text(text, metadata)
