# 🐦 Post Tweet Skill

## Purpose
This skill allows the AI Employee to publish a text-based tweet to the configured Twitter (X) account. This is typically used for sharing short updates, announcements, or engaging with followers.

## Input Parameters
The AI Employee needs the following information to post a tweet:

1.  **`text` (string, required):** The text content of the tweet. Tweets have a character limit enforced by Twitter (currently 280 characters for most users). The AI should ensure the text adheres to this limit.

## Output
Upon successful publication of the tweet, the skill will return:
-   `success` (boolean): `true` if the tweet was posted, `false` otherwise.
-   `tweet_id` (string): The unique ID of the newly created tweet on Twitter.
-   `message` (string): A descriptive message about the outcome.

If the skill fails, it will return:
-   `success` (boolean): `false`.
-   `message` (string): An error message explaining the failure (e.g., "Tweet text too long", "Authentication error", "API rate limit exceeded").

## Execution Steps (Internal AI Logic)
1.  **Validate Inputs:** Ensure `text` is provided and adheres to Twitter's character limit (conceptual, the MCP or API will ultimately enforce this).
2.  **Invoke MCP:** Call `twitter-mcp.post_tweet` with the `text`.
3.  **Handle Response:** Process the response from the MCP, extract `tweet_id` if successful.
4.  **Report Result:** Log the outcome and present the `tweet_id` if successful.

## Example Usage (AI thought process)

**User Request:** "Tweet: 'Just launched a new feature on our platform! Check it out and let us know what you think. #newfeature #innovation'"

**AI Reasoning:**
1.  **Identify Skill:** User wants to post a tweet, so `post_tweet` skill is relevant.
2.  **Extract Parameters:**
    *   `text`: "Just launched a new feature on our platform! Check it out and let us know what you think. #newfeature #innovation"
3.  **Execute Skill (MCP Call):** `twitter-mcp.post_tweet(text="Just launched a new feature on our platform! Check it out and let us know what you think. #newfeature #innovation")`
    *   *Result:* `{'success': true, 'tweet_id': '1234567890123456789', 'message': 'Tweet posted successfully.'}`
4.  **Respond to User:** "I have successfully posted the tweet to your Twitter (X) account. The tweet ID is 1234567890123456789."

## Security & Approval Considerations
-   Tweets are public. The AI should ideally seek human approval for critical or sensitive tweets.
-   Ensure Twitter API credentials (Consumer Key, Consumer Secret, Access Token, Access Token Secret) are securely managed via environment variables.
-   All Twitter interactions are logged by the `twitter-mcp`.
-   The AI should be mindful of Twitter's content policies and best practices.
