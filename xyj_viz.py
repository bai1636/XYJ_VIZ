import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # 最稳：只保存图片，不弹窗，避免 PyCharm 后端报错

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from PIL import Image
import numpy as np


# =========================
# 1. 自动寻找中文字体
# =========================
def find_chinese_font():
    candidates = [
        "C:/Windows/Fonts/simhei.ttf",      # 黑体
        "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",      # 宋体
        "C:/Windows/Fonts/STZHONGS.TTF",    # 华文中宋
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    ]

    for font_path in candidates:
        if Path(font_path).exists():
            return font_path
    return None


font_path = find_chinese_font()

if font_path:
    try:
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rcParams["font.sans-serif"] = [font_name]
    except Exception:
        pass

plt.rcParams["axes.unicode_minus"] = False


# =========================
# 2. 读取《西游记》文本
# =========================
def read_text(file_path):
    encodings = ["utf-8", "gb18030", "gbk", "gb2312"]

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


file_path = "西游记.txt"
text = read_text(file_path)


# =========================
# 3. 人物别名归并表
# =========================
name_alias = {
    "孙悟空": ["孙悟空", "孙行者", "行者", "悟空", "美猴王", "齐天大圣", "弼马温", "斗战胜佛", "猴王", "老孙"],
    "唐僧": ["唐僧", "唐三藏", "三藏", "玄奘", "唐长老", "御弟圣僧"],
    "猪八戒": ["猪八戒", "八戒", "猪悟能", "悟能", "天蓬元帅", "净坛使者"],
    "沙僧": ["沙僧", "沙和尚", "沙悟净", "悟净", "卷帘大将", "金身罗汉"],
    "白龙马": ["白龙马", "小白龙", "玉龙三太子", "敖烈"],

    "如来佛祖": ["如来佛祖", "如来", "释迦如来"],
    "观音菩萨": ["观音菩萨", "观音", "南海观音", "观世音菩萨"],
    "弥勒佛": ["弥勒佛", "弥勒", "东来佛祖"],
    "太上老君": ["太上老君", "老君"],
    "玉皇大帝": ["玉皇大帝", "玉帝"],
    "王母娘娘": ["王母娘娘", "王母"],
    "太白金星": ["太白金星"],
    "托塔李天王": ["托塔李天王", "李天王"],
    "哪吒": ["哪吒", "哪吒太子", "哪吒三太子"],
    "二郎神": ["二郎神", "杨戬", "显圣真君"],
    "四大天王": ["四大天王"],
    "增长天王": ["增长天王"],
    "持国天王": ["持国天王"],
    "广目天王": ["广目天王"],
    "多闻天王": ["多闻天王"],
    "赤脚大仙": ["赤脚大仙"],
    "镇元子": ["镇元子", "镇元大仙"],
    "菩提祖师": ["菩提祖师", "须菩提祖师", "祖师"],
    "灵吉菩萨": ["灵吉菩萨"],
    "文殊菩萨": ["文殊菩萨"],
    "普贤菩萨": ["普贤菩萨"],
    "地藏王菩萨": ["地藏王菩萨", "地藏王"],
    "黎山老母": ["黎山老母"],
    "福星": ["福星"],
    "禄星": ["禄星"],
    "寿星": ["寿星"],
    "木吒": ["木吒", "惠岸行者"],
    "金吒": ["金吒"],
    "嫦娥": ["嫦娥", "素娥"],
    "吴刚": ["吴刚"],
    "奎木狼": ["奎木狼"],
    "昴日星官": ["昴日星官"],
    "九天应元雷声普化天尊": ["九天应元雷声普化天尊"],
    "真武大帝": ["真武大帝"],
    "东华帝君": ["东华帝君"],

    "东海龙王": ["东海龙王", "敖广"],
    "南海龙王": ["南海龙王", "敖钦"],
    "西海龙王": ["西海龙王", "敖闰"],
    "北海龙王": ["北海龙王", "敖顺"],

    "牛魔王": ["牛魔王", "平天大圣"],
    "铁扇公主": ["铁扇公主", "罗刹女"],
    "红孩儿": ["红孩儿", "圣婴大王", "善财童子"],
    "黄风怪": ["黄风怪", "黄风大王"],
    "黄袍怪": ["黄袍怪"],
    "黄眉老怪": ["黄眉老怪", "黄眉大王"],
    "黑熊精": ["黑熊精", "黑风怪"],
    "白骨精": ["白骨精", "白骨夫人", "尸魔"],
    "六耳猕猴": ["六耳猕猴"],
    "青牛精": ["青牛精", "独角兕大王"],
    "金角大王": ["金角大王"],
    "银角大王": ["银角大王"],
    "精细鬼": ["精细鬼"],
    "伶俐虫": ["伶俐虫"],
    "九头虫": ["九头虫"],
    "万圣公主": ["万圣公主"],
    "玉兔精": ["玉兔精"],
    "蝎子精": ["蝎子精"],
    "蜘蛛精": ["蜘蛛精", "七个蜘蛛精"],
    "蜈蚣精": ["蜈蚣精", "百眼魔君", "多目怪"],
    "豹子精": ["豹子精"],
    "狮猁怪": ["狮猁怪", "青毛狮子怪"],
    "青狮精": ["青狮精", "青狮"],
    "白象精": ["白象精", "白象"],
    "大鹏金翅雕": ["大鹏金翅雕", "云程万里鹏", "大鹏"],
    "灵感大王": ["灵感大王"],
    "独角鬼王": ["独角鬼王"],
    "混世魔王": ["混世魔王"],
    "虎力大仙": ["虎力大仙"],
    "鹿力大仙": ["鹿力大仙"],
    "羊力大仙": ["羊力大仙"],
    "赛太岁": ["赛太岁"],
    "金毛犼": ["金毛犼"],
    "九灵元圣": ["九灵元圣"],
    "辟寒大王": ["辟寒大王"],
    "辟暑大王": ["辟暑大王"],
    "辟尘大王": ["辟尘大王"],
    "杏仙": ["杏仙"],
    "玉面公主": ["玉面公主"],
    "老鼠精": ["老鼠精", "地涌夫人", "半截观音"],
    "南山大王": ["南山大王"],
    "通天河老鼋": ["老鼋", "通天河老鼋"],

    "乌鸡国国王": ["乌鸡国国王"],
    "乌鸡国太子": ["乌鸡国太子"],
    "宝象国公主": ["百花羞", "百花羞公主"],
    "宝象国国王": ["宝象国国王"],
    "车迟国国王": ["车迟国国王"],
    "比丘国国王": ["比丘国国王"],
    "祭赛国国王": ["祭赛国国王"],
    "朱紫国国王": ["朱紫国国王"],
    "女儿国国王": ["女儿国国王"],
    "灭法国国王": ["灭法国国王"],
    "凤仙郡侯": ["凤仙郡侯"],

    "陈光蕊": ["陈光蕊"],
    "殷温娇": ["殷温娇", "满堂娇"],
    "刘洪": ["刘洪"],
    "法明长老": ["法明长老"],
    "高翠兰": ["高翠兰"],
    "高太公": ["高太公"],
    "高夫人": ["高夫人"],
    "寇员外": ["寇员外"],
    "金池长老": ["金池长老"],
    "观音院老院主": ["老院主"],
    "唐太宗": ["唐太宗", "李世民"],
    "魏征": ["魏征"],
    "袁守诚": ["袁守诚"],
    "李淳风": ["李淳风"],
    "尉迟恭": ["尉迟恭"],
    "秦叔宝": ["秦叔宝"],
    "阎王": ["阎王", "十殿阎王"],

    "雷公": ["雷公"],
    "电母": ["电母"],
    "风婆": ["风婆"],
    "雨师": ["雨师"],
    "土地": ["土地", "土地公"],
    "山神": ["山神"],
    "揭谛": ["揭谛", "五方揭谛"],
    "金头揭谛": ["金头揭谛"],
    "银头揭谛": ["银头揭谛"],
    "波罗揭谛": ["波罗揭谛"],
    "摩诃揭谛": ["摩诃揭谛"],
    "伽蓝": ["伽蓝"],
    "功曹": ["功曹"],
    "值日神": ["值日神"],
    "六丁六甲": ["六丁六甲"],

    "接引佛祖": ["接引佛祖"],
    "阿傩": ["阿傩"],
    "迦叶": ["迦叶"],
    "燃灯古佛": ["燃灯古佛"]
}

# =========================
# 4. 构造正则表达式
# 为防止短别名覆盖长别名，按长度降序排列
# =========================
alias_to_name = {}
all_aliases = []

for person, aliases in name_alias.items():
    for alias in aliases:
        alias_to_name[alias] = person
        all_aliases.append(alias)

all_aliases = sorted(set(all_aliases), key=len, reverse=True)
pattern = re.compile("|".join(map(re.escape, all_aliases)))


# =========================
# 5. 统计人物频率
# =========================
counter = Counter()

for match in pattern.finditer(text):
    alias = match.group(0)
    person = alias_to_name[alias]
    counter[person] += 1

top15 = counter.most_common(15)


# =========================
# 6. 输出统计结果
# =========================
print("前十五名人物词频统计：")
for i, (name, count) in enumerate(top15, start=1):
    print(f"{i:>2}. {name:<8} {count}")


# =========================
# 7. 保存统计结果到文本文件
# =========================
with open("西游记人物词频统计结果.txt", "w", encoding="utf-8") as f:
    f.write("前十五名人物词频统计：\n")
    for i, (name, count) in enumerate(top15, start=1):
        f.write(f"{i:>2}. {name:<8} {count}\n")


# =========================
# 8. 绘制渐变色柱状图
# =========================
names = [item[0] for item in top15]
counts = [item[1] for item in top15]

plt.figure(figsize=(12, 6))

colors = plt.cm.viridis(np.linspace(0, 0.8, len(names)))   # 渐变色
bars = plt.bar(names, counts, color=colors)

plt.title("《西游记》人物出现频率前十五名")
plt.xlabel("人物")
plt.ylabel("出现次数")
plt.xticks(rotation=45)

for bar, count in zip(bars, counts):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 5,
        str(count),
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()
plt.savefig("西游记人物词频柱状图.png", dpi=300, bbox_inches="tight")
plt.close()


# =========================
# 9. 使用 mask.png 生成更饱满的词云图
# =========================
if font_path is None:
    raise RuntimeError("未找到可用的中文字体，无法生成中文词云图。请检查系统字体。")

mask_path = Path("mask.png")
if not mask_path.exists():
    raise FileNotFoundError("未找到 mask.png，请将其放在当前代码同目录下。")

# 这里尽量取更多人物
wc_dict = dict(counter)

# =========================
# 9. 使用新的 mask.png 生成词云图（最终稳版）
# =========================
from PIL import Image
import numpy as np

if font_path is None:
    raise RuntimeError("未找到可用的中文字体，无法生成中文词云图。")

mask_path = Path("mask.png")
if not mask_path.exists():
    raise FileNotFoundError("未找到 mask.png，请将其放在当前代码同目录下。")

# 读取 mask 并转灰度
mask_img = Image.open(mask_path).convert("L")
mask_arr = np.array(mask_img)

# 关键：把浅灰背景处理成纯白，把猴头处理成纯黑
# 你这张图背景很亮，猴头很黑，所以这样阈值化最稳
mask = np.where(mask_arr > 240, 255, 0).astype(np.uint8)

# 可选：把处理后的 mask 存出来检查
Image.fromarray(mask).save("debug_mask.png")

# 词云尽量多给一些人物，不要只用前15个
wc_dict = dict(counter.most_common(100))

# 自定义颜色（和你的渐变柱状图更协调）
palette = ["#2E86AB", "#3CB371", "#5B5EA6", "#1F77B4", "#2CA02C", "#4E79A7"]

def color_func(*args, **kwargs):
    return np.random.choice(palette)

wordcloud = WordCloud(
    font_path=font_path,
    background_color="white",
    mask=mask,
    max_words=300,
    repeat=True,             # 关键：允许重复高频词填满图形
    prefer_horizontal=0.95,
    relative_scaling=0.2,
    max_font_size=100,
    min_font_size=6,
    margin=1,
    scale=3,
    random_state=42,
    contour_width=0,
    collocations=False
).generate_from_frequencies(wc_dict)

# 重新上色
wordcloud = wordcloud.recolor(color_func=color_func, random_state=42)

plt.figure(figsize=(10, 8), facecolor="white")
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("《西游记》人物词云")
plt.tight_layout()
plt.savefig("西游记人物词云.png", dpi=600, bbox_inches="tight", facecolor="white")
plt.close()

# =========================
# 10. 结束提示
# =========================
print("\n运行完成！已生成以下文件：")
print("1. 西游记人物词频统计结果.txt")
print("2. 西游记人物词频柱状图.png")
print("3. 西游记人物词云.png")