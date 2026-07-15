import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TextVectorizer:
    """Vectorize text for similarity comparison using TF-IDF."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )
        self.is_fitted = False

    def fit(self, texts: List[str]):
        """Fit the vectorizer on a corpus of texts."""
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts into TF-IDF vectors."""
        if not self.is_fitted:
            self.fit(texts)
        return self.vectorizer.transform(texts)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        texts = [text1, text2]
        vectors = self.transform(texts)
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])
        return float(similarity[0][0])

    def rank_by_similarity(
        self,
        query_text: str,
        candidate_texts: List[Tuple[int, str]],
    ) -> List[Tuple[int, float]]:
        """
        Rank candidates by similarity to a query text.

        Args:
            query_text: The job description or query
            candidate_texts: List of (id, text) tuples

        Returns:
            List of (id, score) tuples sorted by score descending
        """
        if not candidate_texts:
            return []

        # Prepare texts
        texts = [query_text] + [ct[1] for ct in candidate_texts]
        ids = [ct[0] for ct in candidate_texts]

        # Vectorize
        vectors = self.transform(texts)

        # Compute similarities
        query_vector = vectors[0:1]
        candidate_vectors = vectors[1:]

        similarities = cosine_similarity(query_vector, candidate_vectors)[0]

        # Create ranked list
        results = [(ids[i], float(similarities[i])) for i in range(len(ids))]
        results.sort(key=lambda x: x[1], reverse=True)

        return results
