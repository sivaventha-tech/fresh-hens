"""
DatasetService — searches and links datasets from Kaggle and HuggingFace.
Actual downloads are deferred to background tasks.
"""
from typing import Optional
from loguru import logger
from app.core.config import settings


class DatasetService:

    async def search_kaggle(self, keywords: list[str]) -> list[dict]:
        """Search Kaggle for relevant datasets. Returns list of dataset info."""
        if not settings.KAGGLE_USERNAME or not settings.KAGGLE_KEY:
            logger.warning("Kaggle credentials not configured — skipping search")
            return []
        try:
            import kaggle
            import asyncio
            query = " ".join(keywords[:3])
            results = await asyncio.to_thread(
                kaggle.api.dataset_list, search=query, sort_by="hottest", max_size=50
            )
            return [
                {
                    "source": "kaggle",
                    "name": str(d),
                    "url": f"https://www.kaggle.com/datasets/{d}",
                    "description": getattr(d, "subtitle", ""),
                }
                for d in results[:5]
            ]
        except Exception as e:
            logger.error(f"Kaggle search failed: {e}")
            return []

    async def search_huggingface(self, keywords: list[str]) -> list[dict]:
        """Search HuggingFace Hub for relevant datasets."""
        try:
            from huggingface_hub import list_datasets
            import asyncio
            query = " ".join(keywords[:3])
            results = await asyncio.to_thread(
                lambda: list(list_datasets(search=query, limit=5))
            )
            return [
                {
                    "source": "huggingface",
                    "name": d.id,
                    "url": f"https://huggingface.co/datasets/{d.id}",
                    "description": getattr(d, "description", ""),
                }
                for d in results
            ]
        except Exception as e:
            logger.error(f"HuggingFace search failed: {e}")
            return []

    async def find_datasets(self, keywords: list[str]) -> dict:
        """Run both searches and return combined results."""
        kaggle_results = await self.search_kaggle(keywords)
        hf_results = await self.search_huggingface(keywords)
        all_results = kaggle_results + hf_results
        logger.info(f"Dataset search: found {len(all_results)} results for {keywords}")
        return {
            "keywords": keywords,
            "results": all_results,
            "kaggle_count": len(kaggle_results),
            "huggingface_count": len(hf_results),
        }


dataset_service = DatasetService()
