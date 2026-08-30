def compress_context(messages,llm):
    compressed_messages = []
    old_history = messages[:-6]
    new_history = messages[-6:]
    # 生成早期历史记录摘要
    old_text = ""
    for h in old_history:
        if h["role"] == 'user':
            old_text += f"问题：{h['content']}\n"
        else:
            old_text += f"回答：{h['content']}\n"
    prompt = f"请将以下对话历史压缩为一段简洁的背景摘要，保留关键事实和用户偏好，不超过300字：\n{old_text}"

    # 调用LLM生成压缩摘要
    summary = llm.invoke(prompt)

    # 将压缩摘要和最新对话追加到历史记录中
    compressed_messages.append({"role": "system", "content":f"[历史对话摘要]: {summary.content}"})    # 打包塞入
    compressed_messages.extend(new_history) # 拆包合并
    return compressed_messages