import asyncio
import logging
import random
import time
import uuid
from fastmcp import FastMCP

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
    delay_seconds: float = 600.0,
) -> str:
    """
    Generates a random image URL after awaiting a specified delay (default 10 minutes / 600 seconds).

    Args:
        prompt: Description or title for the image.
        width: Width of the image in pixels.
        height: Height of the image in pixels.
        delay_seconds: Duration in seconds to await (default: 600 seconds = 10 minutes).

    Returns:
        Formatted markdown text rendering the generated image and details directly in chat.
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

    # Log after image generation / before returning
    logger.info(f"[After Image Return] Returning image URL '{image_url}' (Elapsed: {round(elapsed, 2)}s)")

    return (
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


if __name__ == "__main__":
    logger.info("Starting FastMCP HTTP Server on http://0.0.0.0:8000/mcp ...")
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        host_origin_protection=False,
        allowed_hosts=["*"],
    )
