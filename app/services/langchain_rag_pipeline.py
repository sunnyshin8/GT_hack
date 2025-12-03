"""
LangChain-based RAG (Retrieval Augmented Generation) pipeline for customer support.
Integrates with Google Gemini for embeddings and chat completion.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import asyncio
from datetime import datetime

import numpy as np
import google.generativeai as genai
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

from app.core.cache import cache_get, cache_set
from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.knowledge_base_generator import generate_starbucks_knowledge_base

# Load environment variables
load_dotenv()

logger = get_logger(__name__)
settings = get_settings()

# Configure Google Generative AI
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


class RAGPipeline:
    """LangChain-based RAG pipeline for intelligent customer support."""
    
    def __init__(self):
        """Initialize the RAG pipeline with OpenAI components."""
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.llm = None
        self.rag_chain = None
        self.knowledge_base = []
        self._check_gemini_key()
        
    def _check_gemini_key(self):
        """Check if Google API key is available."""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            logger.info("RAG pipeline will work in fallback mode without Gemini")
        else:
            logger.info(f"Gemini API key loaded successfully (key starts with: {self.gemini_api_key[:8]}...)")
            
    async def initialize(self):
        """Initialize the RAG pipeline components."""
        try:
            logger.info("Initializing LangChain RAG pipeline...")
            
            # Load knowledge base documents
            self.knowledge_base = await self.load_knowledge_base()
            logger.info(f"Loaded {len(self.knowledge_base)} knowledge base documents")
            
            # Initialize Gemini components if API key is available
            if os.getenv("GEMINI_API_KEY"):
                await self._initialize_gemini_components()
            else:
                logger.warning("Gemini components not initialized - API key missing")
                
            logger.info("RAG pipeline initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    
    async def _initialize_gemini_components(self):
        """Initialize Google Gemini embeddings and LLM."""
        try:
            # Configure Google Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            
            # Initialize embeddings with Gemini embedding model
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
            
            # Initialize ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.7,
                google_api_key=api_key,
                convert_system_message_to_human=True
            )
            
            # Create and store vector embeddings
            await self.embed_and_store(self.knowledge_base)
            
            # Set up the RAG chain
            self._setup_rag_chain()
            
            logger.info("Gemini components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini components: {e}")
            raise
    
    async def load_knowledge_base(self) -> List[Document]:
        """Load knowledge base documents and convert to LangChain Documents."""
        try:
            # Generate knowledge base
            kb_data = generate_starbucks_knowledge_base()
            
            documents = []
            for item in kb_data:
                # Create LangChain Document with content and metadata
                doc = Document(
                    page_content=item["content"],
                    metadata={
                        "doc_id": item["doc_id"],
                        "doc_type": item["doc_type"],
                        "store_id": item["store_id"],
                        "category": item["metadata"]["category"],
                        "valid_until": item["metadata"]["valid_until"],
                        "applicable_tier": item["metadata"]["applicable_tier"],
                        "weather_condition": item["metadata"]["weather_condition"]
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    async def embed_and_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents."""
        try:
            if not self.embeddings:
                raise ValueError("Embeddings not initialized")
            
            # Create FAISS vector store
            self.vectorstore = await asyncio.to_thread(
                FAISS.from_documents,
                documents,
                self.embeddings
            )
            
            # Create retriever with k=5
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            logger.info(f"Created FAISS vector store with {len(documents)} documents")
            return self.vectorstore
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def _setup_rag_chain(self):
        """Set up the RAG chain using LangChain Expression Language (LCEL)."""
        try:
            # Define the prompt template
            prompt_template = ChatPromptTemplate.from_template("""
You are a helpful Starbucks customer support assistant. Use the provided context to answer the customer's question.
Be friendly, concise, and accurate. Limit your response to 2-3 sentences for mobile-friendly experience.

Customer Context:
- Name: {customer_name}
- Loyalty Tier: {loyalty_tier} 
- Favorite Categories: {favorite_categories}

Location Context:
- Distance to Store: {distance_to_store}
- Nearest Store: {store_name}
- Weather: {weather}

Retrieved Context:
{context}

Current Time: {current_time}

Customer Question: {question}

Provide a helpful response that:
1. Addresses the specific question
2. Uses relevant information from the context
3. Personalizes the response based on customer and location context
4. Keeps the response concise (2-3 sentences max)
5. Includes specific prices, store details, or promotions when relevant

Response:""")
            
            # Format documents function
            def format_docs(docs):
                return "\n\n".join([
                    f"[{doc.metadata.get('category', 'info')}] {doc.page_content}"
                    for doc in docs
                ])
            
            # Create the RAG chain using LCEL
            self.rag_chain = (
                {
                    "context": self.retriever | format_docs,
                    "customer_name": RunnablePassthrough(),
                    "loyalty_tier": RunnablePassthrough(), 
                    "favorite_categories": RunnablePassthrough(),
                    "distance_to_store": RunnablePassthrough(),
                    "store_name": RunnablePassthrough(),
                    "weather": RunnablePassthrough(),
                    "question": RunnablePassthrough(),
                    "current_time": lambda _: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
            )
            
            logger.info("RAG chain setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup RAG chain: {e}")
            raise
    
    async def retrieve_relevant_docs(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve top-k relevant documents for a query."""
        try:
            if not self.retriever:
                # Fallback: simple text matching if vector store not available
                return await self._fallback_retrieve(query, k)
            
            # Use vector similarity search
            docs = await asyncio.to_thread(self.retriever.get_relevant_documents, query)
            return docs[:k]
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return await self._fallback_retrieve(query, k)
    
    async def _fallback_retrieve(self, query: str, k: int = 5) -> List[Document]:
        """Fallback document retrieval using simple text matching."""
        try:
            query_lower = query.lower()
            scored_docs = []
            
            for doc in self.knowledge_base:
                content_lower = doc.page_content.lower()
                # Simple scoring based on keyword matches
                score = sum(1 for word in query_lower.split() if word in content_lower)
                if score > 0:
                    scored_docs.append((doc, score))
            
            # Sort by score and return top-k
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return [doc for doc, _ in scored_docs[:k]]
            
        except Exception as e:
            logger.error(f"Fallback retrieval failed: {e}")
            return []
    
    async def generate_response(
        self,
        query: str,
        customer_context: Optional[Dict[str, Any]] = None,
        location_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using RAG pipeline."""
        try:
            # Check cache first
            cache_key = f"rag_response:{hash(query)}:{hash(str(customer_context))}:{hash(str(location_context))}"
            cached_response = await cache_get(cache_key)
            if cached_response:
                logger.info("Serving RAG response from cache")
                return cached_response
            
            # Default contexts if not provided
            if customer_context is None:
                customer_context = {
                    "customer_name": "Valued Customer",
                    "loyalty_tier": "bronze", 
                    "favorite_categories": ["coffee", "snacks"]
                }
            
            if location_context is None:
                location_context = {
                    "distance_to_store": "2.5 km",
                    "store_name": "Starbucks Central",
                    "weather": "pleasant"
                }
            
            # Retrieve relevant documents
            relevant_docs = await self.retrieve_relevant_docs(query)
            
            # Generate response
            if self.rag_chain:
                # Use LangChain RAG pipeline with Gemini
                response_text = await asyncio.to_thread(
                    self.rag_chain.invoke,
                    {
                        **customer_context,
                        **location_context, 
                        "question": query
                    }
                )
                confidence = 0.9  # High confidence with Gemini
            else:
                # Fallback response generation
                response_text = await self._generate_fallback_response(
                    query, relevant_docs, customer_context, location_context
                )
                confidence = 0.7  # Lower confidence for fallback
            
            # Prepare sources information
            sources = [
                {
                    "doc_id": doc.metadata.get("doc_id", "unknown"),
                    "doc_type": doc.metadata.get("doc_type", "unknown"),
                    "category": doc.metadata.get("category", "unknown"),
                    "relevance_score": 0.8  # Placeholder score
                }
                for doc in relevant_docs
            ]
            
            result = {
                "response": response_text,
                "sources": sources,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "customer_context": customer_context,
                "location_context": location_context
            }
            
            # Cache the response for 1 hour
            await cache_set(cache_key, result, ttl=3600)
            
            logger.info("RAG response generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate RAG response: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again or visit our store for assistance.",
                "sources": [],
                "confidence": 0.1,
                "error": str(e)
            }
    
    async def _generate_fallback_response(
        self,
        query: str,
        docs: List[Document],
        customer_context: Dict[str, Any],
        location_context: Dict[str, Any]
    ) -> str:
        """Generate fallback response without Gemini."""
        try:
            customer_name = customer_context.get("customer_name", "Valued Customer")
            loyalty_tier = customer_context.get("loyalty_tier", "bronze")
            
            # Simple template-based response
            if docs:
                # Use content from most relevant document
                main_content = docs[0].page_content
                
                # Extract key information
                if "price" in query.lower() or "cost" in query.lower():
                    response = f"Hi {customer_name}! Based on our current pricing, {main_content[:200]}... As a {loyalty_tier} member, you may be eligible for additional discounts!"
                elif "store" in query.lower() or "location" in query.lower():
                    response = f"Hello {customer_name}! {main_content[:150]}... Your nearest store is {location_context.get('store_name', 'Starbucks Central')}."
                elif "promotion" in query.lower() or "offer" in query.lower():
                    response = f"Great question, {customer_name}! {main_content[:180]}... Check our app for {loyalty_tier} member exclusive offers!"
                else:
                    response = f"Hi {customer_name}! {main_content[:200]}... Visit us at your nearest location for more details!"
            else:
                response = f"Hi {customer_name}! Thank you for your question. Please visit our nearest store or call our customer service at 1800-266-0010 for detailed assistance."
            
            # Ensure mobile-friendly length (2-3 sentences max)
            sentences = response.split('. ')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
            
            return response
            
        except Exception as e:
            logger.error(f"Fallback response generation failed: {e}")
            return "I apologize for the inconvenience. Please contact our customer service for assistance."
    
    async def update_knowledge_base(self, new_documents: List[Dict[str, Any]]):
        """Update the knowledge base with new documents."""
        try:
            # Convert to LangChain Documents
            new_docs = []
            for item in new_documents:
                doc = Document(
                    page_content=item["content"],
                    metadata=item.get("metadata", {})
                )
                new_docs.append(doc)
            
            # Add to existing knowledge base
            self.knowledge_base.extend(new_docs)
            
            # Re-create vector store if embeddings available
            if self.embeddings:
                await self.embed_and_store(self.knowledge_base)
                logger.info(f"Updated vector store with {len(new_docs)} new documents")
            
        except Exception as e:
            logger.error(f"Failed to update knowledge base: {e}")
            raise

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()

async def get_rag_response(
    query: str,
    customer_context: Optional[Dict[str, Any]] = None,
    location_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to get RAG response."""
    if not rag_pipeline.knowledge_base:
        await rag_pipeline.initialize()
    
    return await rag_pipeline.generate_response(query, customer_context, location_context)