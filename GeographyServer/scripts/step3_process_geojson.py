import json
from pathlib import Path

# ====== 配置 ======
geojson_root = Path(r"G:\datasets\Geography\echarts-map-demo\全国省市区geoJson数据包\100000")
output_path = Path(r"G:\GitHub\GeographicalKnowledgeQuiz\GeographyServer\processed_data\admin_divisions.txt")

# ====== 省级代码 → 省名映射 ======
province_names = {
    "110000": "北京市", "120000": "天津市", "130000": "河北省", "140000": "山西省",
    "150000": "内蒙古自治区", "210000": "辽宁省", "220000": "吉林省", "230000": "黑龙江省",
    "310000": "上海市", "320000": "江苏省", "330000": "浙江省", "340000": "安徽省",
    "350000": "福建省", "360000": "江西省", "370000": "山东省", "410000": "河南省",
    "420000": "湖北省", "430000": "湖南省", "440000": "广东省", "450000": "广西壮族自治区",
    "460000": "海南省", "500000": "重庆市", "510000": "四川省", "520000": "贵州省",
    "530000": "云南省", "540000": "西藏自治区", "610000": "陕西省", "620000": "甘肃省",
    "630000": "青海省", "640000": "宁夏回族自治区", "650000": "新疆维吾尔自治区",
    "710000": "台湾省", "810000": "香港特别行政区", "820000": "澳门特别行政区"
}

level_map = {
    "country": "国家级", "province": "省级", "city": "市级",
    "district": "区县级", "street": "街道级"
}

# ====== 遍历所有GeoJSON文件 ======
all_records = []
province_dirs = sorted(geojson_root.iterdir())

print(f"找到 {len(province_dirs)} 个省级目录")

for prov_dir in province_dirs:
    if not prov_dir.is_dir():
        continue

    prov_code = prov_dir.name
    prov_name = province_names.get(prov_code, f"未知省份({prov_code})")
    print(f"\n处理 {prov_name} ({prov_code})...")

    geojson_files = list(prov_dir.glob("*.geoJson")) + list(prov_dir.glob("*.json"))
    city_count = 0

    for gj_file in geojson_files:
        try:
            with open(gj_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"  ⚠️ 解析失败 {gj_file.name}: {e}")
            continue

        if data.get('type') != 'FeatureCollection':
            continue

        features = data.get('features', [])
        if not features:
            continue

        city_count += 1

        for feature in features:
            props = feature.get('properties', {})
            name = props.get('name', '')
            adcode = props.get('adcode', '')
            level = props.get('level', '')
            center = props.get('center', [])
            acroutes = props.get('acroutes', [])

            if not name:
                continue

            hierarchy_parts = []
            if len(acroutes) >= 2:
                parent_prov_code = str(acroutes[1]) if isinstance(acroutes[1], int) else acroutes[1]
                parent_prov_name = province_names.get(parent_prov_code, "")
                if parent_prov_name:
                    hierarchy_parts.append(parent_prov_name)
            if len(acroutes) >= 3:
                parent_city_code = str(acroutes[2]) if isinstance(acroutes[2], int) else acroutes[2]
                hierarchy_parts.append(f"{parent_city_code}")

            level_cn = level_map.get(level, level)

            line = f"{name}"
            if adcode:
                line += f"（行政区划代码：{adcode}）"
            line += f"，行政级别：{level_cn}"
            if hierarchy_parts:
                line += f"，隶属于：{'-'.join(hierarchy_parts)}"
            if center and isinstance(center, list) and len(center) == 2:
                line += f"，中心坐标：经度{center[0]}°，纬度{center[1]}°"

            all_records.append(line)

    print(f"  {city_count} 个市级文件")

# ====== 合并省级 + 区县级，去重 ======
province_lines = []
for code, name in sorted(province_names.items()):
    province_lines.append(f"{name}（行政区划代码：{code}），行政级别：省级")

all_output = province_lines + all_records

seen = set()
unique_output = []
for line in all_output:
    if line not in seen:
        seen.add(line)
        unique_output.append(line)

print(f"\n===== 汇总 =====")
print(f"省级: {len(province_lines)} 条")
print(f"区县级: {len(all_records)} 条")
print(f"去重后总计: {len(unique_output)} 条")

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(unique_output))

print(f"✅ 已写入 {output_path}")

print(f"\n===== 前10条样例 =====")
for line in unique_output[:10]:
    print(line)