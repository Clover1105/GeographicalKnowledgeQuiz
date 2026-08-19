import fitz  # PyMuPDF
from pathlib import Path

# ====== 配置 ======
china_textbook_root = Path(r"G:\datasets\Geography\ChinaTextbook")
output_dir = Path(r"G:\GitHub\GeographicalKnowledgeQuiz\GeographyServer\processed_data\textbooks_text")

# 失败的两个文件（手动指定路径）
failed_pdfs = [
    china_textbook_root / "初中" / "地理" / "人教版-人民教育出版社" / "七年级" / "义务教育教科书·地理七年级下册.pdf",
    china_textbook_root / "初中" / "地理" / "人教版-人民教育出版社" / "八年级" / "义务教育教科书·地理八年级下册.pdf",
]

for pdf_path in failed_pdfs:
    print(f"\n{'='*60}")
    print(f"用 PyMuPDF 重试: {pdf_path.name}")

    if not pdf_path.exists():
        print(f"  ⚠️ 文件不存在: {pdf_path}")
        continue

    text_parts = []
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        print(f"  总页数: {total_pages}")

        for i, page in enumerate(doc):
            text = page.get_text("text")
            if text and len(text.strip()) > 10:
                text_parts.append(f"[第{i+1}页]\n{text}")

            if (i + 1) % 20 == 0:
                print(f"  已处理 {i+1}/{total_pages} 页...")

        doc.close()

        if text_parts:
            stage = "初中"
            stem = pdf_path.stem
            simple_name = f"{stage}_人教版_{stem}.txt"
            simple_name = simple_name.replace('义务教育教科书·地理', '').strip('_') + '.txt'

            out_file = output_dir / simple_name
            full_text = "\n\n".join(text_parts)
            out_file.write_text(full_text, encoding="utf-8")

            size_kb = len(full_text.encode('utf-8')) / 1024
            print(f"  ✅ {len(text_parts)}/{total_pages} 页有效 → {simple_name} ({size_kb:.0f} KB)")
        else:
            print(f"  ❌ PyMuPDF 也无法提取文字，确实是纯扫描版PDF")
            print(f"     需要 OCR 处理（小型项目可跳过，不影响整体效果）")

    except Exception as e:
        print(f"  ❌ 错误: {e}")