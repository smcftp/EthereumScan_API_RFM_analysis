import copy
import base64
import logging
import requests
from io import BytesIO
from typing import Optional

from article import utils as article_utils
from article.agent import generate_article
from article.image_generation import ImageGenerator

from .config import wp_config
from . import utils


class WordpressUploader:
    """Uploads post or media to your Wordpress site."""

    def __init__(self):
        credentials: str = wp_config.WP_USER + ":" + wp_config.WP_PASSWORD
        self._token: bytes = base64.b64encode(credentials.encode())

    @property
    def headers(self) -> dict:
        return {
            "Authorization": "Basic " + self._token.decode('utf-8')
        }

    @property
    def media_headers(self) -> dict:
        media_headers = copy.deepcopy(self.headers)
        media_headers.update({"Content-Disposition": f"attachment; filename=image.jpg"})
        return media_headers

    @property
    def wp_post_url(self) -> str:
        return wp_config.WP_URL + "posts"

    @property
    def wp_media_url(self) -> str:
        return wp_config.WP_URL + "media"

    def upload_post(self, title: str, post: str) -> Optional[int]:
        response = requests.post(
            self.wp_post_url,
            headers=self.headers,
            json={
                "title": title,
                "content": post,
                "status": "publish"
            }
        )
        return utils.wordpress_response_handler(response=response, action="upload", entity="post")

    def upload_image(self, image: BytesIO | None) -> Optional[int]:
        if not image:
            return
        response = requests.post(
            url=wp_config.WP_URL + "media",
            headers=self.media_headers,
            files={"file": ("image.jpg", image, 'image/jpeg')},
        )
        return utils.wordpress_response_handler(response=response, action="upload", entity="media")

    def update_post_with_media(self, post_id: int, media_id: int) -> Optional[int]:
        url = f"{self.wp_post_url}/{post_id}"
        response = requests.post(
            url=url,
            headers=self.headers,
            json={
                "featured_media": media_id
            }
        )
        return utils.wordpress_response_handler(response=response, action="update", entity="post")


def make_post(query: str):
    """Main function to make a post"""
    wp_uploader = WordpressUploader()
    post = generate_article(query=query)
    if not article_utils.is_html(post):
        logging.critical("Unfortunately post wasn't generated. Generated text is not HTML :( ")
        logging.info(post)
        return
    title, post = article_utils.extract_title_from_content(content=post)
    post_id = wp_uploader.upload_post(title=title, post=post)
    image = ImageGenerator().generate(image_query=title)
    media_id = wp_uploader.upload_image(image=image)
    if post_id and media_id:
        wp_uploader.update_post_with_media(post_id=post_id, media_id=media_id)