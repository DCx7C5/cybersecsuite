import random


async def get_minimal_state(page):
    visible_text = await page.evaluate(r"""
() => {
    return document.body.innerText
        .replace(/\s+/g, ' ')
        .trim()
        .slice(0, 6000);
}
""")

    return {
        "type": "tool_result",
        "content": {
            "url": page.url,
            "title": await page.title(),
            "text": visible_text,
            "status": "ready"
        }
    }
