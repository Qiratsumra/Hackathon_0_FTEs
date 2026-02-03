# 📸 Post Instagram Image Skill

## Purpose
This skill allows the AI Employee to publish an image with an optional caption to a specified Instagram Business or Creator Account. This is typically used for visual content sharing and engagement.

## Input Parameters
The AI Employee needs the following information to post an Instagram image:

1.  **`ig_user_id` (string, required):** The ID of the Instagram Business or Creator Account where the image should be posted. This ID must correspond to an account accessible by the configured `INSTAGRAM_ACCESS_TOKEN`.
2.  **`image_url` (string, required):** A publicly accessible URL of the image to be posted. Instagram's API requires the image to be hosted externally and publicly reachable.
3.  **`caption` (string, optional):** The text caption for the Instagram post.

## Output
Upon successful publication of the Instagram image, the skill will return:
-   `success` (boolean): `true` if the image was posted, `false` otherwise.
-   `media_id` (string): The unique ID of the newly created media item on Instagram.
-   `message` (string): A descriptive message about the outcome.

If the skill fails, it will return:
-   `success` (boolean): `false`.
-   `message` (string): An error message explaining the failure (e.g., "Invalid image URL", "Authentication error", "Instagram API limitations").

## Execution Steps (Internal AI Logic)
1.  **Validate Inputs:** Ensure `ig_user_id` and `image_url` are provided. Verify `image_url` is publicly accessible (conceptual, AI may not have direct tools for this and rely on MCP error).
2.  **Invoke MCP:** Call `facebook-instagram-mcp.post_image_to_instagram_business_account` with `ig_user_id`, `image_url`, and `caption`.
3.  **Handle Response:** Process the response from the MCP, extract `media_id` if successful.
4.  **Report Result:** Log the outcome and present the `media_id` if successful.

## Example Usage (AI thought process)

**User Request:** "Post this image to Instagram with the caption 'Our new office space! #worklife #newbeginnings' Image URL: https://example.com/new_office.jpg"

**AI Reasoning:**
1.  **Identify Skill:** User wants to post an image to Instagram, so `post_instagram_image` skill is relevant.
2.  **Extract Parameters:**
    *   `ig_user_id`: (Needs to be determined by AI or pre-configured in AI's context, e.g., "Our Instagram Business Account ID")
    *   `image_url`: "https://example.com/new_office.jpg"
    *   `caption`: "Our new office space! #worklife #newbeginnings"
3.  **Execute Skill (MCP Call):** `facebook-instagram-mcp.post_image_to_instagram_business_account(ig_user_id="Our Instagram Business Account ID", image_url="https://example.com/new_office.jpg", caption="Our new office space! #worklife #newbeginnings")`
    *   *Result:* `{'success': true, 'media_id': '178901234567890', 'message': 'Posted image to Instagram.'}`
4.  **Respond to User:** "I have successfully posted the image to your Instagram Business Account. The media ID is 178901234567890."

## Security & Approval Considerations
-   Similar to Facebook posts, Instagram posts are public. The AI should ideally seek human approval for critical or sensitive image posts.
-   Ensure `INSTAGRAM_ACCESS_TOKEN` is securely managed via environment variables.
-   All Instagram interactions are logged by the `facebook-instagram-mcp`.
-   Note the Instagram API limitations regarding content types (e.g., no direct Reels/Stories via API) and frequency limits.
