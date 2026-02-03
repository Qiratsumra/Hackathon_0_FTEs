# ✍️ Create Facebook Post Skill

## Purpose
This skill allows the AI Employee to publish a text message or a link post to a specified Facebook Page. This is typically used for sharing updates, announcements, or promotional content.

## Input Parameters
The AI Employee needs the following information to create a Facebook post:

1.  **`page_id` (string, required):** The ID of the Facebook Page where the post should be published. This ID must correspond to a page accessible by the configured `FB_PAGE_ACCESS_TOKEN`.
2.  **`message` (string, required):** The text content of the post.
3.  **`link` (string, optional):** A URL to attach to the post. This will typically generate a link preview on Facebook.

## Output
Upon successful creation of the Facebook post, the skill will return:
-   `success` (boolean): `true` if the post was created, `false` otherwise.
-   `post_id` (string): The unique ID of the newly created post on Facebook.
-   `message` (string): A descriptive message about the outcome.

If the skill fails, it will return:
-   `success` (boolean): `false`.
-   `message` (string): An error message explaining the failure (e.g., "Page not found", "Authentication error", "API rate limit exceeded").

## Execution Steps (Internal AI Logic)
1.  **Validate Inputs:** Ensure `page_id` and `message` are provided.
2.  **Invoke MCP:** Call `facebook-instagram-mcp.post_to_facebook_page` with `page_id`, `message`, and `link`.
3.  **Handle Response:** Process the response from the MCP, extract `post_id` if successful.
4.  **Report Result:** Log the outcome and present the `post_id` if successful.

## Example Usage (AI thought process)

**User Request:** "Post an announcement to our Facebook page: 'Exciting new product launch coming soon! Stay tuned for updates: www.ourwebsite.com/newproduct'"

**AI Reasoning:**
1.  **Identify Skill:** User wants to post to Facebook, so `create_facebook_post` skill is relevant.
2.  **Extract Parameters:**
    *   `page_id`: (Needs to be determined by AI or pre-configured in AI's context, e.g., "Our Company Page ID")
    *   `message`: "Exciting new product launch coming soon! Stay tuned for updates."
    *   `link`: "www.ourwebsite.com/newproduct"
3.  **Execute Skill (MCP Call):** `facebook-instagram-mcp.post_to_facebook_page(page_id="Our Company Page ID", message="Exciting new product launch coming soon! Stay tuned for updates.", link="https://www.ourwebsite.com/newproduct")`
    *   *Result:* `{'success': true, 'post_id': '123456789_987654321', 'message': 'Posted to Facebook Page.'}`
4.  **Respond to User:** "I have successfully posted the announcement to your Facebook page. The post ID is 123456789_987654321."

## Security & Approval Considerations
-   Posting to social media has public visibility. The AI should exercise caution and ideally operate under a human-in-the-loop approval mechanism for critical or sensitive posts (e.g., if a post is generated autonomously by the AI based on an event, it might require approval via the `approval_creator` skill before final publication).
-   Ensure `FB_PAGE_ACCESS_TOKEN` is securely managed via environment variables and never exposed.
-   All Facebook interactions are logged by the `facebook-instagram-mcp`.
