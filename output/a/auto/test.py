import json

def extract_blocks_for_vectorization(blocks):
    """
    提取可用于向量化的文本内容，包括正文、标题和图注。
    """
    vector_blocks = []

    for block in blocks:
        if block["type"] == "text":
            content = block["text"].strip()
            if content:
                vector_blocks.append({
                    "page": block["page_idx"],
                    "bbox": block.get("bbox"),
                    "type": "text",
                    "content": content
                })

        elif block["type"] == "image" and "image_caption" in block:
            captions = " ".join(block["image_caption"]).strip()
            if captions:
                vector_blocks.append({
                    "page": block["page_idx"],
                    "bbox": block.get("bbox"),
                    "type": "image_caption",
                    "content": captions
                })

    return vector_blocks


# 示例用法
with open("a_content_list.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vector_blocks = extract_blocks_for_vectorization(data)

for i  in range(10):
    print(vector_blocks[i])
