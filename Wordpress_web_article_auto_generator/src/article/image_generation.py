from io import BytesIO
import requests
from typing import Optional

import logging
from openai import OpenAI, BadRequestError
from PIL import Image

from .config import config
from .prompts import help_image_prompt


class ImageGenerator:
    """Generates images using OpenAI API."""

    def __init__(self, max_retries: int = 5):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.max_retries = max_retries

    def generate(self, image_query: str) -> Optional[BytesIO]:
        """Generates an image for the post"""

        for num in range(self.max_retries):
            image_query = self._rephrase_image_query(image_query=image_query)
            logging.info(f"Image query: {image_query}")
            try:
                logging.info(f"Generating image attempt #{num+1}")
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=image_query,
                    size="1792x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                image_bytes = self._download_image(image_url)
                if image_bytes:
                    image_bytes = self._compress_image(image_bytes=image_bytes, max_size_mb=2.0)
                    return image_bytes
            except BadRequestError as error:
                if error.code == "content_policy_violation":
                    logging.error("CONTENT POLICY VIOLATION ERROR !")
                else:
                    logging.error(error)
        logging.error("Image generation failed :(")
        return None

    def _rephrase_image_query(self, image_query: str) -> str:
        """Rephrases the image query to avoid content policy violations"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": help_image_prompt.prompt.format(query=image_query)}
            ],
            max_tokens=100,
            n=1,
        )
        rephrased_query = response.choices[0].message.content
        return rephrased_query

    @staticmethod
    def _download_image(image_url: str) -> Optional[BytesIO]:
        """Downloads image from the given URL and returns as BytesIO"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_bytes = BytesIO(response.content)
            image_bytes.seek(0)
            return image_bytes
        except requests.RequestException as e:
            logging.error(f"Error downloading image: {e}")
            return None

    @staticmethod
    def _compress_image(image_bytes: BytesIO, max_size_mb: float) -> BytesIO:
        """Compresses the image to ensure it meets the maximum size requirements"""
        image = Image.open(image_bytes)
        output = BytesIO()
        quality = 95
        while True:
            output.seek(0)
            image.save(output, format="JPEG", quality=quality)
            size_mb = output.tell() / (1024 * 1024)
            if size_mb <= max_size_mb or quality <= 10:
                break
            quality -= 5
        output.seek(0)
        return output