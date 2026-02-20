"""
Gemini Embedding-based Symptom Mapper with Vector Database
Uses Google's Gemini API for embeddings and ChromaDB for vector storage
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiSymptomMapper:
    """
    Maps custom symptoms using Gemini embeddings and ChromaDB vector database
    
    Features:
    - One-time embedding generation
    - Persistent vector storage
    - Fast similarity search
    - Free tier friendly
    """
    
    def __init__(
        self,
        csv_path: Optional[str] = None,
        collection_name: str = "symptom_embeddings",
        similarity_threshold: float = 0.7,
        db_path: Optional[str] = None
    ):
        """
        Initialize the Gemini-based symptom mapper
        
        Args:
            csv_path: Path to Custom_Symptom.csv
            collection_name: Name for ChromaDB collection
            similarity_threshold: Minimum similarity score (0-1)
            db_path: Path to ChromaDB storage (default: backend/data/chroma_db)
        """
        # Setup paths
        if csv_path is None:
            backend_dir = Path(__file__).parent.parent.parent
            csv_path = backend_dir / "data" / "Custom_Symptom.csv"
        self.csv_path = Path(csv_path)
        
        if db_path is None:
            backend_dir = Path(__file__).parent.parent.parent
            db_path = backend_dir / "data" / "chroma_db"
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Load symptoms data
        self.symptoms_df: Optional[pd.DataFrame] = None
        self._load_symptoms()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info("GeminiSymptomMapper initialized successfully")
    
    def _load_symptoms(self):
        """Load symptoms from CSV file"""
        try:
            self.symptoms_df = pd.read_csv(self.csv_path, encoding='utf-8')
            logger.info(f"Loaded {len(self.symptoms_df)} symptoms from {self.csv_path}")
        except FileNotFoundError:
            logger.error(f"Symptom file not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading symptoms: {e}")
            raise
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """
        Get existing collection or create new one with embeddings
        Returns:
            ChromaDB collection
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self._get_embedding_function()
            )
            logger.info(f"Using existing collection '{self.collection_name}' with {collection.count()} embeddings")
            return collection
        except Exception as e:
            logger.info(f"Collection not found or invalid: {e}")
        # Create new collection and populate it
        logger.info("Creating new collection with embeddings...")
        collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self._get_embedding_function(),
            metadata={"description": "Custom symptom embeddings using Gemini"}
        )
        self._populate_collection(collection)
        return collection
    
    def _get_embedding_function(self):
        """Get ChromaDB embedding function using Gemini"""
        class GeminiEmbeddingFunction:
            def __call__(self, input: List[str]) -> List[List[float]]:
                """Generate embeddings for a list of texts"""
                return self.embed_documents(input)

            def embed_documents(self, input: List[str]) -> List[List[float]]:
                embeddings = []
                for text in input:
                    result = genai.embed_content(
                        model="gemini-embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(result['embedding'])
                return embeddings

            def embed_query(self, input: str) -> List[float]:
                """Generate embedding for a single query text"""
                result = genai.embed_content(
                    model="gemini-embedding-001",
                    content=input,
                    task_type="retrieval_query"
                )
                return result['embedding']

        return GeminiEmbeddingFunction()
    
    def _populate_collection(self, collection: chromadb.Collection):
        """
        Populate collection with symptom embeddings (one-time operation)
        
        Args:
            collection: ChromaDB collection to populate
        """
        logger.info("Generating embeddings for all symptoms...")
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in self.symptoms_df.iterrows():
            symptom_id = str(row['ID'])
            symptom_text = str(row['Symptoms'])
            
            documents.append(symptom_text)
            ids.append(symptom_id)
            
            # Store metadata
            metadata = {
                'symptom': symptom_text,
                'risk_level': str(row['Risk level']).strip(),
                'recommendation': str(row.get('Recommendation', '')).strip(),
                'management': str(row.get('Management', '')).strip(),
                'symptom_notes': str(row.get('symptom notes', '')).strip()
            }
            metadatas.append(metadata)
        
        # Add to collection (ChromaDB will auto-generate embeddings)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully added {len(documents)} symptom embeddings to collection")
    
    def _embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text"""
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=text,
            task_type="retrieval_query"  # Use query task type for search
        )
        return result['embedding']
    
    def find_similar_symptom(
        self,
        custom_symptom: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find most similar symptoms using vector similarity search
        
        Args:
            custom_symptom: User-reported symptom text
            top_k: Number of top matches to return
            
        Returns:
            List of match results with similarity scores
        """
        # Query the collection
        results = self.collection.query(
            query_texts=[custom_symptom],
            n_results=top_k
        )
        
        matches = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                symptom_id = results['ids'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Convert distance to similarity (ChromaDB uses L2 distance)
                # Normalize to 0-1 range (smaller distance = higher similarity)
                similarity = 1 / (1 + distance)
                
                if similarity >= self.similarity_threshold:
                    match_data = {
                        'id': int(symptom_id),
                        'symptom': metadata['symptom'],
                        'similarity': float(similarity),
                        'distance': float(distance),
                        'metadata': metadata
                    }
                    matches.append(match_data)
                    
                    logger.info(
                        f"Match: '{custom_symptom}' -> '{metadata['symptom']}' "
                        f"(similarity: {similarity:.3f}, distance: {distance:.3f})"
                    )
        
        if not matches:
            logger.info(f"No match above threshold for: '{custom_symptom}'")
        
        return matches
    
    def map_symptom(
        self,
        custom_symptom: str,
        language: str = 'th'
    ) -> Dict[str, Any]:
        """
        Map a custom symptom and return risk assessment
        
        Args:
            custom_symptom: User-reported symptom
            language: Response language ('th' or 'en')
            
        Returns:
            Risk assessment dict
        """
        matches = self.find_similar_symptom(custom_symptom, top_k=1)
        
        if not matches:
            return {
                'risk_level': 'ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน',
                'reason': f'มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {custom_symptom}' if language == 'th' 
                         else f'Additional symptoms reported: {custom_symptom}',
                'recommendation': 'ควรปรึกษาพยาบาลหรือทันตแพทย์เพื่อประเมินอาการเพิ่มเติม' if language == 'th'
                                else 'Talk to your nurse or dentist for a check-up',
                'management': '',
                'matched': False,
                'similarity': 0.0,
                'matched_symptom': '',
                'matched_id': 0
            }
        
        # Get best match
        match = matches[0]
        metadata = match['metadata']
        
        # Map risk level
        risk_level_raw = metadata['risk_level']
        risk_level_map = {
            'ต่ำ': 'ความเสี่ยงต่ำ',
            'ปานกลาง': 'ความเสี่ยงปานกลาง',
            'สูง': 'ความเสี่ยงสูง',
            'ซับซ้อน': 'ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน'
        }
        risk_level = risk_level_map.get(risk_level_raw, 'ความเสี่ยงต่ำ')
        
        # Get recommendation and management
        recommendation = metadata['recommendation']
        if recommendation in ['', 'nan']:
            recommendation = ''
            
        management = metadata['management']
        if management in ['', 'nan']:
            management = ''
        
        # Build reason
        if language == 'en':
            reason = f'Custom symptom "{custom_symptom}" matched to "{match["symptom"]}" (similarity: {match["similarity"]:.2f})'
        else:
            reason = f'อาการที่ระบุ "{custom_symptom}" ตรงกับ "{match["symptom"]}" (ความคล้ายคลึง: {match["similarity"]:.2f})'
        
        return {
            'risk_level': risk_level,
            'reason': reason,
            'recommendation': recommendation,
            'management': management,
            'matched': True,
            'similarity': match['similarity'],
            'matched_symptom': match['symptom'],
            'matched_id': match['id']
        }
    
    def map_multiple_symptoms(
        self,
        custom_symptoms: List[str],
        language: str = 'th'
    ) -> List[Dict[str, Any]]:
        """Map multiple custom symptoms"""
        results = []
        for symptom in custom_symptoms:
            if symptom and symptom.strip():
                result = self.map_symptom(symptom.strip(), language)
                results.append(result)
        return results
    
    def reset_database(self):
        """Reset the vector database (delete and recreate)"""
        logger.warning("Resetting database...")
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise


# Global instance
_mapper_instance: Optional[GeminiSymptomMapper] = None


def get_symptom_mapper(
    similarity_threshold: float = 0.7,
    force_reload: bool = False
) -> GeminiSymptomMapper:
    """Get or create global mapper instance"""
    global _mapper_instance
    
    if _mapper_instance is None or force_reload:
        logger.info("Creating new GeminiSymptomMapper instance")
        _mapper_instance = GeminiSymptomMapper(
            similarity_threshold=similarity_threshold
        )
    
    return _mapper_instance


# Convenience functions
def reload_symptom_collection():
    """Convenience function to reload symptom collection (reset embeddings)"""
    mapper = get_symptom_mapper(force_reload=True)
    mapper.reload_collection()
    return mapper
def map_custom_symptom(
    symptom: str,
    language: str = 'th',
    similarity_threshold: float = 0.7
) -> Dict[str, Any]:
    """Map a single custom symptom"""
    mapper = get_symptom_mapper(similarity_threshold=similarity_threshold)
    return mapper.map_symptom(symptom, language)


def map_custom_symptoms(
    symptoms: List[str],
    language: str = 'th',
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Map multiple custom symptoms"""
    mapper = get_symptom_mapper(similarity_threshold=similarity_threshold)
    return mapper.map_multiple_symptoms(symptoms, language)


if __name__ == "__main__":
    # Test the mapper
    print("=" * 80)
    print("Testing Gemini Symptom Mapper with ChromaDB")
    print("=" * 80)
    
    test_symptoms = [
        "ปากแห้งมาก",
    ]
    
    print(f"\nTesting {len(test_symptoms)} symptoms...")
    results = map_custom_symptoms(test_symptoms, language='th')
    
    for i, (symptom, result) in enumerate(zip(test_symptoms, results), 1):
        print(f"\n--- Test {i}: {symptom} ---")
        print(f"Matched: {result['matched']}")
        print(f"Similarity: {result['similarity']:.3f}")
        print(f"Matched to: {result.get('matched_symptom', 'N/A')}")
        print(f"Risk Level: {result['risk_level']}")
        if result['recommendation']:
            print(f"Recommendation: {result['recommendation']}")
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)
