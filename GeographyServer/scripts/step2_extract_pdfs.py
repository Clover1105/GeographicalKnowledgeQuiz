import pdfplumber
from pathlib import Path
import re

# ====== 配置 ======
china_textbook_root = Path(r"G:\datasets\Geography\ChinaTextbook")
output_dir = Path(r"G:\GitHub\GeographicalKnowledgeQuiz\GeographyServer\processed_data\textbooks_text")
output_dir.mkdir(parents=True, exist_ok=True)

# 只处理人教版（最通用，避免多版本重复）
target_publishers = ["人教版"]

# ====== 查找目标PDF ======
all_pdfs = list(china_textbook_root.rglob("*.pdf"))
complete_pdfs = [p for p in all_pdfs if p.suffix == '.pdf']

geo_pdfs = []
for p in complete_pdfs:
    path_str = str(p)
    is_geo = "地理" in path_str
    is_target = any(pub in path_str for pub in target_publishers)
    if is_geo and is_target:
        geo_pdfs.append(p)

geo_pdfs.sort(key=lambda p: str(p))

print(f"找到 {len(geo_pdfs)} 个目标PDF:")
for p in geo_pdfs:
    rel = p.relative_to(china_textbook_root)
    print(f"  {rel}  ({p.stat().st_size / 1024 / 1024:.1f} MB)")

# ====== 逐个提取文本 ======
success = 0
failed = []

for pdf_path in geo_pdfs:
    print(f"\n{'='*60}")
    print(f"处理: {pdf_path.name}")

    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  总页数: {total_pages}")

            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and len(text.strip()) > 10:
                    text_parts.append(f"[第{i+1}页]\n{text}")

                if (i + 1) % 20 == 0:
                    print(f"  已处理 {i+1}/{total_pages} 页...")

        if text_parts:
            rel_path = pdf_path.relative_to(china_textbook_root)
            parts = rel_path.parts
            stage = parts[0]
            stem = pdf_path.stem
            simple_name = f"{stage}_人教版_{stem}.txt"
            simple_name = re.sub(r'[·\s]+', '_', simple_name)
            simple_name = simple_name.replace('义务教育教科书_地理', '').replace('普通高中教科书_地理', '')
            simple_name = simple_name.strip('_') + '.txt'

            out_file = output_dir / simple_name
            full_text = "\n\n".join(text_parts)
            out_file.write_text(full_text, encoding="utf-8")

            size_kb = len(full_text.encode('utf-8')) / 1024
            print(f"  ✅ {len(text_parts)}/{total_pages} 页有效 → {simple_name} ({size_kb:.0f} KB)")
            success += 1
        else:
            print(f"  ⚠️ 未提取到文字（可能是扫描版PDF）")
            failed.append(pdf_path.name)

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        failed.append(pdf_path.name)

print(f"\n{'='*60}")
print(f"===== 完成 =====")
print(f"成功: {success}, 失败/跳过: {len(failed)}")
if failed:
    print(f"跳过的文件: {failed}")

total_chars = 0
for txt_file in output_dir.glob("*.txt"):
    total_chars += len(txt_file.read_text(encoding='utf-8'))
print(f"总文本量: {total_chars:,} 字符 ({total_chars/10000:.1f} 万字)")