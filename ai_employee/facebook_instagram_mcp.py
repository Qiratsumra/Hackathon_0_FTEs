import os
import json
import logging
import requests
# Consider using a more robust Facebook SDK if available and well-maintained
# For now, direct requests are used as a flexible approach.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s')
logger = logging.getLogger(__name__)

class FacebookInstagramMCP:
    def __init__(self):
        self.FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN") # May be the same as FB Page Access Token for IG Business accounts
        self.FACEBOOK_GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0" # Use a specific version
        
        if not self.FB_PAGE_ACCESS_TOKEN and not self.INSTAGRAM_ACCESS_TOKEN:
            logger.error("Neither FB_PAGE_ACCESS_TOKEN nor INSTAGRAM_ACCESS_TOKEN provided in environment variables.")
            raise ValueError("Missing Facebook/Instagram API access tokens.")

    def _make_graph_api_call(self, endpoint, method="GET", params=None, data=None, headers=None):
        """Helper to make calls to Facebook Graph API."""
        url = f"{self.FACEBOOK_GRAPH_API_BASE_URL}/{endpoint}"
        
        # Ensure access token is always included
        if method == "GET":
            params = params if params is not None else {}
            if "access_token" not in params:
                params["access_token"] = self.FB_PAGE_ACCESS_TOKEN # Assume FB token for FB calls
        elif method == "POST":
            data = data if data is not None else {}
            if "access_token" not in data:
                data["access_token"] = self.FB_PAGE_ACCESS_TOKEN # Assume FB token for FB calls
        
        try:
            response = requests.request(method, url, params=params, json=data, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            raise

    def post_to_facebook_page(self, page_id: str, message: str, link: str = None) -> dict:
        """
        Posts a message to a specific Facebook Page.
        :param page_id: The ID of the Facebook Page.
        :param message: The message text to post.
        :param link: Optional URL to attach to the post.
        :return: Dictionary with post ID if successful.
        """
        if not self.FB_PAGE_ACCESS_TOKEN:
            return {"success": False, "message": "FB_PAGE_ACCESS_TOKEN not configured."}

        endpoint = f"{page_id}/feed"
        data = {"message": message}
        if link:
            data["link"] = link

        try:
            logger.info(f"Posting message to Facebook Page {page_id}...")
            response = self._make_graph_api_call(endpoint, method="POST", data=data)
            logger.info(f"Successfully posted to Facebook Page {page_id}. Post ID: {response.get('id')}")
            return {"success": True, "post_id": response.get("id"), "message": "Posted to Facebook Page."}
        except Exception as e:
            logger.error(f"Failed to post to Facebook Page {page_id}: {e}")
            return {"success": False, "message": str(e)}

    def post_image_to_instagram_business_account(self, ig_user_id: str, image_url: str, caption: str = "") -> dict:
        """
        Posts an image to an Instagram Business or Creator Account.
        This is a two-step process: create container, then publish.
        :param ig_user_id: The Instagram Business Account ID.
        :param image_url: Publicly accessible URL of the image.
        :param caption: Optional caption for the image.
        :return: Dictionary with media ID if successful.
        """
        if not self.INSTAGRAM_ACCESS_TOKEN:
            return {"success": False, "message": "INSTAGRAM_ACCESS_TOKEN not configured."}

        # Step 1: Create media container
        container_endpoint = f"{ig_user_id}/media"
        container_params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.INSTAGRAM_ACCESS_TOKEN # Use IG token for IG calls
        }
        try:
            logger.info(f"Creating Instagram media container for {ig_user_id}...")
            container_response = self._make_graph_api_call(container_endpoint, method="POST", params=container_params)
            creation_id = container_response.get("id")
            if not creation_id:
                raise Exception(f"Failed to get creation_id: {container_response}")
            logger.info(f"Instagram media container created with ID: {creation_id}")

            # Step 2: Publish media container
            publish_endpoint = f"{ig_user_id}/media_publish"
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.INSTAGRAM_ACCESS_TOKEN # Use IG token for IG calls
            }
            logger.info(f"Publishing Instagram media for {ig_user_id}...")
            publish_response = self._make_graph_api_call(publish_endpoint, method="POST", params=publish_params)
            media_id = publish_response.get("id")
            if not media_id:
                raise Exception(f"Failed to get media_id: {publish_response}")
            logger.info(f"Successfully posted image to Instagram. Media ID: {media_id}")
            return {"success": True, "media_id": media_id, "message": "Posted image to Instagram."}

        except Exception as e:
            logger.error(f"Failed to post image to Instagram Business Account {ig_user_id}: {e}")
            return {"success": False, "message": str(e)}

    def get_facebook_page_posts(self, page_id: str, limit: int = 5) -> list:
        """
        Retrieves recent posts from a Facebook Page.
        :param page_id: The ID of the Facebook Page.
        :param limit: Number of posts to retrieve.
        :return: List of post dictionaries.
        """
        if not self.FB_PAGE_ACCESS_TOKEN:
            return [{"success": False, "message": "FB_PAGE_ACCESS_TOKEN not configured."}]

        endpoint = f"{page_id}/posts"
        params = {"fields": "id,message,created_time,permalink_url", "limit": limit}
        
        try:
            logger.info(f"Retrieving {limit} posts from Facebook Page {page_id}...")
            response = self._make_graph_api_call(endpoint, params=params)
            posts = response.get("data", [])
            logger.info(f"Successfully retrieved {len(posts)} posts from Facebook Page {page_id}.")
            return posts
        except Exception as e:
            logger.error(f"Failed to retrieve posts from Facebook Page {page_id}: {e}")
            return [{"success": False, "message": str(e)}]

    def get_instagram_media(self, ig_user_id: str, limit: int = 5) -> list:
        """
        Retrieves recent media from an Instagram Business or Creator Account.
        :param ig_user_id: The Instagram Business Account ID.
        :param limit: Number of media items to retrieve.
        :return: List of media dictionaries.
        """
        if not self.INSTAGRAM_ACCESS_TOKEN:
            return [{"success": False, "message": "INSTAGRAM_ACCESS_TOKEN not configured."}]

        endpoint = f"{ig_user_id}/media"
        params = {"fields": "id,caption,media_type,media_url,permalink,timestamp", "limit": limit, "access_token": self.INSTAGRAM_ACCESS_TOKEN}
        
        try:
            logger.info(f"Retrieving {limit} media items from Instagram Account {ig_user_id}...")
            response = self._make_graph_api_call(endpoint, params=params)
            media_items = response.get("data", [])
            logger.info(f"Successfully retrieved {len(media_items)} media items from Instagram Account {ig_user_id}.")
            return media_items
        except Exception as e:
            logger.error(f"Failed to retrieve media from Instagram Account {ig_user_id}: {e}")
            return [{"success": False, "message": str(e)}]

if __name__ == "__main__":
    # Example usage (requires environment variables to be set)
    # os.environ["FB_PAGE_ACCESS_TOKEN"] = "YOUR_FB_PAGE_ACCESS_TOKEN"
    # os.environ["INSTAGRAM_ACCESS_TOKEN"] = "YOUR_INSTAGRAM_ACCESS_TOKEN" # Often the same as FB_PAGE_ACCESS_TOKEN
    # os.environ["FB_PAGE_ID"] = "YOUR_FACEBOOK_PAGE_ID"
    # os.environ["IG_BUSINESS_ACCOUNT_ID"] = "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID"

    try:
        mcp = FacebookInstagramMCP()

        # Example: Post to Facebook Page
        # fb_page_id = os.getenv("FB_PAGE_ID")
        # if fb_page_id:
        #     print("\n--- Posting to Facebook Page ---")
        #     fb_post_result = mcp.post_to_facebook_page(
        #         page_id=fb_page_id,
        #         message="Hello from AI Employee MCP! This is a test post with a link.",
        #         link="https://www.example.com"
        #     )
        #     print(f"Facebook Post Result: {fb_post_result}")
        # else:
        #     print("FB_PAGE_ID not set, skipping Facebook post example.")

        # Example: Post image to Instagram Business Account
        # ig_business_account_id = os.getenv("IG_BUSINESS_ACCOUNT_ID")
        # if ig_business_account_id:
        #     print("\n--- Posting Image to Instagram ---")
        #     # Ensure this image URL is publicly accessible
        #     ig_post_result = mcp.post_image_to_instagram_business_account(
        #         ig_user_id=ig_business_account_id,
        #         image_url="https://www.nasa.gov/sites/default/files/thumbnails/image/main_image_star-forming_region_carina_nircam_final-5mb.jpg",
        #         caption="Stunning nebula image posted by AI Employee MCP! #space #nasa"
        #     )
        #     print(f"Instagram Post Result: {ig_post_result}")
        # else:
        #     print("IG_BUSINESS_ACCOUNT_ID not set, skipping Instagram post example.")

        # Example: Get Facebook Page Posts
        # fb_page_id = os.getenv("FB_PAGE_ID")
        # if fb_page_id:
        #     print("\n--- Getting Facebook Page Posts ---")
        #     fb_posts = mcp.get_facebook_page_posts(page_id=fb_page_id, limit=2)
        #     for post in fb_posts:
        #         print(f"FB Post ID: {post.get('id')}, Message: {post.get('message', 'N/A')[:50]}...")
        # else:
        #     print("FB_PAGE_ID not set, skipping Facebook posts example.")

        # Example: Get Instagram Media
        # ig_business_account_id = os.getenv("IG_BUSINESS_ACCOUNT_ID")
        # if ig_business_account_id:
        #     print("\n--- Getting Instagram Media ---")
        #     ig_media = mcp.get_instagram_media(ig_user_id=ig_business_account_id, limit=2)
        #     for media in ig_media:
        #         print(f"IG Media ID: {media.get('id')}, Caption: {media.get('caption', 'N/A')[:50]}...")
        # else:
        #     print("IG_BUSINESS_ACCOUNT_ID not set, skipping Instagram media example.")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except requests.exceptions.RequestException as re:
        print(f"Network or API Request Error: {re}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
