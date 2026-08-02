import asyncio
import base64
import logging
import random
import time
import uuid
import httpx
from fastmcp import FastMCP
from mcp.types import ImageContent, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ImageGeneratorServer")

# Initialize FastMCP Server
mcp = FastMCP("Image Generator Server")


@mcp.tool()
async def generate_image(
    prompt: str = "random photo",
    width: int = 800,
    height: int = 600,
    delay_seconds: float = 0,
) -> list:
    """
    Generates a random image and returns both native MCP ImageContent and formatted Markdown text.

    Args:
        prompt: Description or title for the image.
        width: Width of the image in pixels.
        height: Height of the image in pixels.
        delay_seconds: Duration in seconds to await (default: 0 seconds).

    Returns:
        A list containing ImageContent (for native chat UI image rendering) and TextContent.
    """
    logger.info(f"[Incoming Request] Tool 'generate_image' called: prompt='{prompt}', size={width}x{height}, delay_seconds={delay_seconds}")
    start_time = time.time()

    # Log before async sleep
    if delay_seconds > 0:
        logger.info(f"[Before Async Sleep] Awaiting {delay_seconds} seconds ({round(delay_seconds / 60, 2)} minutes)...")
        await asyncio.sleep(delay_seconds)
        logger.info(f"[After Async Sleep] Finished awaiting {delay_seconds} seconds.")

    end_time = time.time()
    elapsed = end_time - start_time

    # Generate unique random image URL from Picsum Photos
    random_seed = str(uuid.uuid4())[:8]
    image_id = random.randint(1, 1000)
    image_url = f"https://picsum.photos/id/{image_id}/{width}/{height}?random={random_seed}"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    contents = []

    # Fetch actual image binary data so MCP client renders native inline ImageContent
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(image_url)
            if resp.status_code == 200:
                b64_data = base64.b64encode(resp.content).decode("utf-8")
                mime_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                contents.append(
                    ImageContent(
                        type="image",
                        data=b64_data,
                        mimeType=mime_type,
                    )
                )
                logger.info(f"[Image Fetch Success] Fetched {len(resp.content)} bytes from {image_url}")
            else:
                logger.warning(f"[Image Fetch Failed] HTTP status {resp.status_code}")
    except Exception as e:
        logger.error(f"[Image Fetch Error] Failed to download image: {e}")

    text_markdown = (
        f"## Generated Image\n\n"
        f"![{prompt}]({image_url})\n\n"
        f"**Details:**\n"
        f"- **Prompt:** {prompt}\n"
        f"- **Resolution:** {width}x{height} px\n"
        f"- **Requested Delay:** {delay_seconds} seconds ({round(delay_seconds / 60, 1)} minutes)\n"
        f"- **Actual Execution Time:** {round(elapsed, 2)} seconds\n"
        f"- **Image URL:** [{image_url}]({image_url})\n"
        f"- **Timestamp:** {timestamp}\n"
    )

    contents.append(TextContent(type="text", text=text_markdown))

    logger.info(f"[After Image Return] Returning image payload (Elapsed: {round(elapsed, 2)}s)")
    return contents


if __name__ == "__main__":
    logger.info("Starting FastMCP HTTP Server on http://0.0.0.0:8000/mcp ...")
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        host_origin_protection=False,
        allowed_hosts=["*"],
    )
