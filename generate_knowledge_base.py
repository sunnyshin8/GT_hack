"""
Script to generate and save the knowledge base JSON file.
"""
import asyncio
from app.services.knowledge_base_generator import save_knowledge_base_to_file

async def main():
    """Generate knowledge base and save to file."""
    print("🚀 Generating Starbucks Knowledge Base...")
    
    try:
        kb = save_knowledge_base_to_file()
        print(f"✅ Successfully generated knowledge base with {len(kb)} documents")
        print("📄 Knowledge base saved to 'starbucks_knowledge_base.json'")
        
        # Display summary
        print("\n📊 Document Categories:")
        categories = {}
        for doc in kb:
            category = doc["metadata"]["category"]
            doc_type = doc["doc_type"]
            key = f"{doc_type} ({category})"
            categories[key] = categories.get(key, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"  • {category}: {count}")
            
    except Exception as e:
        print(f"❌ Error generating knowledge base: {e}")

if __name__ == "__main__":
    asyncio.run(main())