import json
import os

# ====== 配置 ======
data_dir = r"G:\datasets\Geography\baike_qa2019"
output_path = r"G:\GitHub\GeographicalKnowledgeQuiz\GeographyServer\processed_data\qa_baike_geo.jsonl"

# 地理相关关键词（匹配 category 字段中的任意一级）
geo_keywords = [
    '地理', '地球科学', '地质', '气象', '气候', '地形', '水文',
    '自然地理', '人文地理', '行政区划', '海洋学', '天文', '环境科学',
    '生态', '土壤', '矿物', '岩石', '地震', '火山', '冰川',
    '河流', '湖泊', '山脉', '高原', '盆地', '平原', '岛屿',
    '天文学', '地球', '大气', '洋流', '季风', '经纬', '时区',
    '人口地理', '经济地理', '区域地理', '世界地理', '中国地理',
    '地图', '遥感', 'GIS', '自然资源', '环境保护', '灾害'
]

# ====== 处理 ======
results = []
total = 0
files = ['baike_qa_train.json', 'baike_qa_valid.json']

for fname in files:
    fpath = os.path.join(data_dir, fname)
    if not os.path.exists(fpath):
        print(f"⚠️ 文件不存在: {fpath}")
        continue

    print(f"处理 {fname}...")
    count = 0

    with open(fpath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                if line_num <= 5:
                    print(f"  ⚠️ 第{line_num}行JSON解析失败，跳过")
                continue

            total += 1
            category = str(record.get('category', ''))

            if any(kw in category for kw in geo_keywords):
                question = record.get('title', '').strip()
                desc = record.get('desc', '').strip()
                if desc and desc != question:
                    question = f"{question}\n{desc}"

                answer = record.get('answer', '').strip()

                if not question or not answer:
                    continue

                results.append({
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "source": "baike_qa2019"
                })
                count += 1

    print(f"  该文件地理相关: {count} 条")

print(f"\n===== 汇总 =====")
print(f"总记录数: {total}")
print(f"地理相关: {len(results)} 条")

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f"✅ 已写入 {output_path}")

print(f"\n===== 前3条样例 =====")
for r in results[:3]:
    print(json.dumps(r, ensure_ascii=False, indent=2))
    print("---")