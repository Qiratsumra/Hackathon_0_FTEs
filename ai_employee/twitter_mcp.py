import os
import json
import logging
import tweepy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s')
logger = logging.getLogger(__name__)

class TwitterMCP:
    def __init__(self):
        self.CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
        self.CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
        self.ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        self.ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if not all([self.CONSUMER_KEY, self.CONSUMER_SECRET, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET]):
            logger.error("Twitter API credentials not fully provided in environment variables.")
            raise ValueError("Missing Twitter API configuration environment variables.")

        self._client = self._authenticate()

    def _authenticate(self):
        """Authenticates with the Twitter API v2 using Tweepy."""
        try:
            client = tweepy.Client(
                consumer_key=self.CONSUMER_KEY,
                consumer_secret=self.CONSUMER_SECRET,
                access_token=self.ACCESS_TOKEN,
                access_token_secret=self.ACCESS_TOKEN_SECRET
            )
            logger.info("Successfully authenticated with Twitter API.")
            return client
        except Exception as e:
            logger.error(f"Failed to authenticate with Twitter API: {e}")
            raise

    def post_tweet(self, text: str) -> dict:
        """
        Posts a tweet to Twitter.
        :param text: The text content of the tweet.
        :return: Dictionary with tweet ID if successful.
        """
        if not self._client:
            return {"success": False, "message": "Not authenticated with Twitter."}

        try:
            logger.info(f"Attempting to post tweet: {text[:50]}...")
            response = self._client.create_tweet(text=text)
            tweet_id = response.data.get("id")
            if tweet_id:
                logger.info(f"Tweet posted successfully. Tweet ID: {tweet_id}")
                return {"success": True, "tweet_id": tweet_id, "message": "Tweet posted successfully."}
            else:
                logger.error(f"Failed to post tweet: {response.errors}")
                return {"success": False, "message": f"Failed to post tweet: {response.errors}"}
        except Exception as e:
            logger.error(f"An error occurred while posting tweet: {e}")
            return {"success": False, "message": str(e)}

    def get_user_tweets(self, username: str, limit: int = 5) -> list:
        """
        Retrieves recent tweets from a specific user's timeline.
        Note: This requires specific user scopes/permissions in your Twitter app.
        :param username: The username of the user.
        :param limit: The maximum number of tweets to retrieve.
        :return: List of tweet dictionaries.
        """
        if not self._client:
            return [{"success": False, "message": "Not authenticated with Twitter."}]

        try:
            logger.info(f"Retrieving {limit} tweets from @{username}...")
            # First, get user ID from username
            user_response = self._client.get_user(username=username)
            user_id = user_response.data.get("id") if user_response.data else None

            if not user_id:
                logger.warning(f"Could not find user with username: {username}")
                return [{"success": False, "message": f"User @{username} not found."}]

            # Then, get tweets by user ID
            tweets_response = self._client.get_users_tweets(id=user_id, tweet_fields=["created_at", "text"], max_results=limit)
            
            tweets = []
            if tweets_response.data:
                for tweet in tweets_response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None
                    })
            logger.info(f"Retrieved {len(tweets)} tweets from @{username}.")
            return tweets
        except Exception as e:
            logger.error(f"An error occurred while retrieving tweets for @{username}: {e}")
            return [{"success": False, "message": str(e)}]

if __name__ == "__main__":
    # Example usage (requires environment variables to be set)
    # os.environ["TWITTER_CONSUMER_KEY"] = "YOUR_CONSUMER_KEY"
    # os.environ["TWITTER_CONSUMER_SECRET"] = "YOUR_CONSUMER_SECRET"
    # os.environ["TWITTER_ACCESS_TOKEN"] = "YOUR_ACCESS_TOKEN"
    # os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = "YOUR_ACCESS_TOKEN_SECRET"

    try:
        mcp = TwitterMCP()

        # Example: Post a tweet
        # print("\n--- Posting a Tweet ---")
        # tweet_result = mcp.post_tweet("Hello from AI Employee Twitter MCP! #GeminiCLI #Hackathon")
        # print(f"Tweet Result: {tweet_result}")

        # Example: Get user tweets
        # print("\n--- Getting User Tweets ---")
        # username_to_fetch = "Gemini" # Replace with a valid username
        # user_tweets = mcp.get_user_tweets(username=username_to_fetch, limit=3)
        # for tweet in user_tweets:
        #     print(f"Tweet ID: {tweet.get('id')}, Text: {tweet.get('text', 'N/A')[:50]}...")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except tweepy.TweepyException as te:
        print(f"Twitter API Error: {te}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
