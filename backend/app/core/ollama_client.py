import ollama
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self):
        # Connect to Ollama Docker service
        self.client = ollama.Client(host='ollama:11434')
        self.model = "qwen3:8b"  # Use qwen3 for text cleaning
    
    async def ensure_model_available(self) -> bool:
        """Ensure qwen3 model is available"""
        try:
            logger.info(f"Checking if {self.model} is available")
            models = await asyncio.to_thread(self.client.list)
            available_models = [model['name'] for model in models.get('models', [])]
            logger.info(f"Available models: {available_models}")
            
            if self.model in available_models:
                logger.info(f"✅ {self.model} is already available")
                return True
            
            # Pull qwen3 if not available
            logger.info(f"🔄 Pulling {self.model}...")
            await asyncio.to_thread(self.client.pull, self.model)
            logger.info(f"✅ Successfully pulled {self.model}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ensuring model availability: {e}")
            return False
    
    async def clean_text(self, text: str, content_type: str) -> Optional[str]:
        """Clean and structure text using qwen3 model"""
        if not await self.ensure_model_available():
            logger.error(f"Failed to load text cleaning model: {self.model}")
            return None
        
        try:
            logger.info(f"🤖 Starting text cleaning with {self.model}")
            logger.info(f"📊 Input text length: {len(text)} characters")
            
            # Create appropriate cleaning prompt based on content type
            if content_type == 'application/pdf':
                prompt = f"""
                Clean and structure the following PDF extracted text. Remove any formatting artifacts, 
                fix any extraction errors, and organize content in a readable format. 
                Return only the cleaned, well-structured content without any additional commentary.
                
                Text to clean:
                {text[:8000]}
                """
            elif content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                prompt = f"""
                Clean and structure the following spreadsheet data. Remove any formatting issues, 
                ensure data consistency, and organize it in a readable tabular format. 
                Return only the cleaned, well-structured content without any additional commentary.
                
                Text to clean:
                {text[:8000]}
                """
            else:
                prompt = f"""
                Clean and structure the following extracted text. Remove any formatting artifacts, 
                fix any errors, and organize content in a readable format. 
                Return only the cleaned, well-structured content without any additional commentary.
                
                Text to clean:
                {text[:8000]}
                """
            
            # Send to AI for cleaning
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            cleaned_text = response['message']['content'].strip()
            logger.info(f"✅ Successfully cleaned text from {len(text)} to {len(cleaned_text)} characters")
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"❌ Error cleaning text: {e}")
            return None


# Create singleton instance
ollama_client = OllamaClient()
