from langchain_core.embeddings import Embeddings

import logging
from typing import List, Optional


class QwenVLEmbeddingsWrapper(Embeddings):
    """Wrapper to make Qwen3-VL-Embedding-2B compatible with LangChain.

    This model supports text, image, and multimodal embeddings.
    For standard text embeddings, use embed_documents/embed_query.
    For image/multimodal, use the specialized methods.
    """

    BATCH_SIZE = 16  # Conservative batch size for memory efficiency on CPU

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-VL-Embedding-2B",
        device: str = "cpu",
        torch_dtype: Optional[str] = None
    ):
        """Initialize Qwen VL Embedding model.

        Args:
            model_name: HuggingFace model identifier
            device: Device to run on ('cpu', 'cuda', 'mps')
            torch_dtype: Torch dtype ('float32', 'float16', 'bfloat16'). 
                        Defaults to float32 for CPU, float16 for GPU.
        """
        import torch
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

        self.model_name = model_name
        self.device = device

        # Set appropriate dtype based on device
        if torch_dtype:
            self._torch_dtype = getattr(torch, torch_dtype)
        else:
            self._torch_dtype = torch.float32 if device == "cpu" else torch.float16

        logging.info(f"Loading Qwen VL Embedding model: {model_name} on {device}")

        self.processor = AutoProcessor.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=self._torch_dtype,
            device_map=device,
            low_cpu_mem_usage=True
        )
        self.model.eval()

        logging.info(f"Qwen VL Embedding model loaded successfully")

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        import torch

        inputs = self.processor(text=text, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # Use last hidden state and mean pool
            hidden_states = outputs.hidden_states[-1]
            embeddings = hidden_states.mean(dim=1).squeeze()

        return embeddings.cpu().numpy().tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents with automatic batching."""
        import torch

        try:
            all_embeddings = []

            for i in range(0, len(texts), self.BATCH_SIZE):
                batch = texts[i:i + self.BATCH_SIZE]
                logging.debug(f"Embedding batch {i // self.BATCH_SIZE + 1}/{(len(texts) - 1) // self.BATCH_SIZE + 1} ({len(batch)} texts)")

                for text in batch:
                    embedding = self._get_text_embedding(text)
                    all_embeddings.append(embedding)

                # Clear CUDA cache if using GPU
                if self.device != "cpu" and torch.cuda.is_available():
                    torch.cuda.empty_cache()

            return all_embeddings
        except Exception as e:
            logging.error(f"Error embedding documents with Qwen VL: {e}")
            return []

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        try:
            return self._get_text_embedding(text)
        except Exception as e:
            logging.error(f"Error embedding query with Qwen VL: {e}")
            return []

    def embed_image(self, image_path: str) -> List[float]:
        """Embed a single image.

        Args:
            image_path: Path to the image file

        Returns:
            List of floats representing the image embedding
        """
        import torch
        from PIL import Image

        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                hidden_states = outputs.hidden_states[-1]
                embeddings = hidden_states.mean(dim=1).squeeze()

            return embeddings.cpu().numpy().tolist()
        except Exception as e:
            logging.error(f"Error embedding image with Qwen VL: {e}")
            return []

    def embed_multimodal(self, text: str, image_path: str) -> List[float]:
        """Embed text and image together (multimodal embedding).

        Args:
            text: Text description or query
            image_path: Path to the image file

        Returns:
            List of floats representing the multimodal embedding
        """
        import torch
        from PIL import Image

        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(
                text=text,
                images=image,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                hidden_states = outputs.hidden_states[-1]
                embeddings = hidden_states.mean(dim=1).squeeze()

            return embeddings.cpu().numpy().tolist()
        except Exception as e:
            logging.error(f"Error embedding multimodal with Qwen VL: {e}")
            return []