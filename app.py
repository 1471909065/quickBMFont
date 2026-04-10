import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageColor
import io
import zipfile
import os
import math

# --- 多语言支持定义 ---
LANG_MAP = {
    "zh": {
        "title": "🚀 位图制作工具",
        "subtitle": "上传字体 ➜ 实时预览 ➜ 一键导出 BMFont",
        "lang_label": "语言 / Language",
        "style_settings": "🎨 样式设置",
        "font_size": "字体大小",
        "text_color": "文字颜色",
        "bg_type": "背景类型",
        "bg_transparent": "透明",
        "bg_solid": "纯色",
        "bg_color": "背景颜色",
        "advanced_effects": "✨ 高级效果",
        "stroke_width": "描边宽度",
        "stroke_color": "描边颜色",
        "enable_shadow": "启用阴影",
        "shadow_x": "阴影偏移 X",
        "shadow_y": "阴影偏移 Y",
        "shadow_color": "阴影颜色",
        "export_settings": "📦 导出设置",
        "gen_atlas": "生成雪碧图 (Atlas + .fnt)",
        "force_pow2": "强制 2 的幂次方尺寸",
        "upload_section": "1. 上传字体文件 (.ttf, .otf)",
        "input_section": "2. 输入字符",
        "preview_section": "3. 实时预览",
        "atlas_preview": "查看雪碧图预览",
        "export_section": "4. 导出结果",
        "dl_all_btn": "打包下载全部资源",
        "dl_link_text": "点击这里下载 ZIP (包含单图 + Atlas + .fnt)",
        "error_prefix": "发生错误: ",
        "info_msg": "💡 请先上传字体并输入字符。",
        "char_count": "字符",
        "atlas_caption": "雪碧图预览 (纹理集)"
    },
    "en": {
        "title": "🚀 Bitmap Maker",
        "subtitle": "Upload Font ➜ Real-time Preview ➜ Export BMFont",
        "lang_label": "Language",
        "style_settings": "🎨 Style Settings",
        "font_size": "Font Size",
        "text_color": "Text Color",
        "bg_type": "Background Type",
        "bg_transparent": "Transparent",
        "bg_solid": "Solid Color",
        "bg_color": "Background Color",
        "advanced_effects": "✨ Advanced Effects",
        "stroke_width": "Stroke Width",
        "stroke_color": "Stroke Color",
        "enable_shadow": "Enable Shadow",
        "shadow_x": "Shadow Offset X",
        "shadow_y": "Shadow Offset Y",
        "shadow_color": "Shadow Color",
        "export_settings": "📦 Export Settings",
        "gen_atlas": "Generate Atlas (Atlas + .fnt)",
        "force_pow2": "Force Power of 2 Size",
        "upload_section": "1. Upload Font (.ttf, .otf)",
        "input_section": "2. Input Characters",
        "preview_section": "3. Real-time Preview",
        "atlas_preview": "View Atlas Preview",
        "export_section": "4. Export Results",
        "dl_all_btn": "Download All Resources",
        "dl_link_text": "Click here to download ZIP (Individual + Atlas + .fnt)",
        "error_prefix": "Error: ",
        "info_msg": "💡 Please upload a font and input characters first.",
        "char_count": "Chars",
        "atlas_caption": "Texture Atlas Preview"
    }
}

# --- 逻辑状态初始化 ---
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

def t(key):
    return LANG_MAP[st.session_state.lang].get(key, key)

# --- 页面配置 ---
st.set_page_config(
    page_title=f"{t('title')} - Premium",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 米色调 UI CSS ---
st.markdown(f"""
    <style>
    /* 全局背景 */
    .stApp {{
        background-color: #FBF9F1;
        color: #2D2D2D;
    }}
    /* 侧边栏 */
    [data-testid="stSidebar"] {{
        background-color: #F1EFE3;
        border-right: 1px solid #E5E1D1;
    }}
    /* 按钮样式 */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        background-color: #D4A373;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #BC8A5F;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 163, 115, 0.3);
    }}
    /* 卡片样式 */
    .char-card {{
        background: white;
        border: 1px solid #E5E1D1;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }}
    .char-card:hover {{
        transform: scale(1.05);
        border-color: #D4A373;
    }}
    /* 预览背景 */
    .preview-bg {{
        background-image: linear-gradient(45deg, #f0f0f0 25%, transparent 25%), 
                          linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), 
                          linear-gradient(45deg, transparent 75%, #f0f0f0 75%), 
                          linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
        background-size: 20px 20px;
        background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        border-radius: 8px;
        padding: 10px;
    }}
    /* 标题颜色 */
    h1, h2, h3 {{
        color: #4A4A4A !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 核心逻辑：渲染字符 ---
def render_char(char, font, text_color, bg_color, stroke_width, stroke_color, shadow_offset, shadow_color):
    mask = font.getmask(char)
    bbox = mask.getbbox()
    
    if not bbox:
        width = font.getlength(char)
        return None, {
            "id": ord(char), "x": 0, "y": 0, "width": 0, "height": 0,
            "xoffset": 0, "yoffset": 0, "xadvance": int(width),
            "page": 0, "chnl": 15
        }

    xadvance = int(font.getlength(char))
    
    # 冗余画布，防止切边
    canvas_w = int(font.size * 2 + stroke_width * 2 + abs(shadow_offset[0]) * 2 + 20)
    canvas_h = int(font.size * 2 + stroke_width * 2 + abs(shadow_offset[1]) * 2 + 20)
    
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    if bg_color != "Transparent":
        bg_img = Image.new("RGBA", (canvas_w, canvas_h), ImageColor.getrgb(bg_color))
        img = Image.alpha_composite(img, bg_img)
        
    draw = ImageDraw.Draw(img)
    draw_x, draw_y = canvas_w // 2, canvas_h // 2
    
    if any(shadow_offset):
        draw.text((draw_x + shadow_offset[0], draw_y + shadow_offset[1]), char, font=font, fill=shadow_color)
    draw.text((draw_x, draw_y), char, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)
    
    final_bbox = img.getbbox()
    if final_bbox:
        img = img.crop(final_bbox)
        metadata = {
            "id": ord(char), "width": img.width, "height": img.height,
            "xoffset": final_bbox[0] - draw_x, "yoffset": final_bbox[1] - draw_y,
            "xadvance": xadvance, "page": 0, "chnl": 15
        }
        return img, metadata
    return None, None

def create_atlas(char_data, padding=2, force_pow2=True):
    if not char_data: return None, ""
    chars = sorted(char_data, key=lambda x: x['img'].height, reverse=True)
    total_area = sum(c['img'].width * c['img'].height for c in chars) * 1.3
    target_width = int(math.sqrt(total_area))
    if force_pow2:
        target_width = 2**math.ceil(math.log2(target_width))
    
    current_x, current_y = 0, 0
    max_row_h = 0
    max_w = 0
    for c in chars:
        if current_x + c['img'].width + padding > target_width:
            current_x, current_y = 0, current_y + max_row_h + padding
            max_row_h = 0
        c['atlas_x'], c['atlas_y'] = current_x, current_y
        current_x += c['img'].width + padding
        max_row_h, max_w = max(max_row_h, c['img'].height), max(max_w, current_x)
    
    final_h = current_y + max_row_h
    if force_pow2:
        final_h = 2**math.ceil(math.log2(final_h))
        max_w = target_width
    atlas_img = Image.new("RGBA", (max_w, final_h), (0, 0, 0, 0))
    for c in chars:
        atlas_img.paste(c['img'], (c['atlas_x'], c['atlas_y']))
    return atlas_img, chars

def generate_fnt_text(font_name, size, atlas_w, atlas_h, chars_with_pos):
    lines = [
        f'info face="{font_name}" size={size} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
        f'common lineHeight={size} base={int(size*0.8)} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0',
        f'page id=0 file="font.png"',
        f'chars count={len(chars_with_pos)}'
    ]
    for c in chars_with_pos:
        m = c['meta']
        lines.append(f"char id={m['id']:<4} x={c['atlas_x']:<5} y={c['atlas_y']:<5} width={m['width']:<5} height={m['height']:<5} xoffset={int(m['xoffset']):<5} yoffset={int(m['yoffset']):<5} xadvance={m['xadvance']:<5} page=0  chnl=15")
    return "\n".join(lines)

# --- 顶部导航与语言切换 ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.title(t("title"))
with header_col2:
    selected_lang = st.selectbox(
        "", # 隐藏 label
        options=["中文", "English"],
        index=0 if st.session_state.lang == "zh" else 1,
        key="lang_toggle"
    )
    st.session_state.lang = "zh" if selected_lang == "中文" else "en"

st.markdown(f"*{t('subtitle')}*")

# --- UI 侧边栏 ---
st.sidebar.title(t("style_settings"))
font_size = st.sidebar.slider(t("font_size"), 10, 512, 128)
text_color = st.sidebar.color_picker(t("text_color"), "#2D2D2D")
bg_color_type = st.sidebar.radio(t("bg_type"), [t("bg_transparent"), t("bg_solid")])
bg_color = "Transparent"
if bg_color_type == t("bg_solid"):
    bg_color = st.sidebar.color_picker(t("bg_color"), "#FFFFFF")

st.sidebar.markdown("---")
st.sidebar.subheader(t("advanced_effects"))
stroke_width = st.sidebar.slider(t("stroke_width"), 0, 20, 0)
stroke_color = st.sidebar.color_picker(t("stroke_color"), "#D4A373")
enable_shadow = st.sidebar.checkbox(t("enable_shadow"), value=False)
shadow_x = st.sidebar.slider(t("shadow_x"), -20, 20, 2) if enable_shadow else 0
shadow_y = st.sidebar.slider(t("shadow_y"), -20, 20, 2) if enable_shadow else 0
shadow_color = st.sidebar.color_picker(t("shadow_color"), "#888888") if enable_shadow else "#888888"

st.sidebar.markdown("---")
st.sidebar.subheader(t("export_settings"))
export_atlas = st.sidebar.checkbox(t("gen_atlas"), value=True)
force_pow2 = st.sidebar.checkbox(t("force_pow2"), value=False)

# --- 默认字体配置 ---
DEFAULT_FONT_PATH = r"D:\开发工具\位图制作\乐米波波体.ttf"

# --- 主界面内容 ---
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_font = st.file_uploader(t("upload_section"), type=["ttf", "otf"])
with col2:
    text_input = st.text_area(t("input_section"), "0123456789% ", height=100)

# 确定最终使用的字体
selected_font = None
is_default = False

if uploaded_font:
    selected_font = uploaded_font
elif os.path.exists(DEFAULT_FONT_PATH):
    selected_font = DEFAULT_FONT_PATH
    is_default = True

if selected_font and text_input:
    try:
        font = ImageFont.truetype(selected_font, font_size)
        
        if is_default:
            st.success(f"✅ 使用默认字体: {os.path.basename(DEFAULT_FONT_PATH)}")
            
        unique_chars = sorted(list(set(text_input)))
        st.markdown(f"### {t('preview_section')} ({len(unique_chars)} {t('char_count')})")
        
        char_results, invisible_chars = [], []
        for char in unique_chars:
            img, meta = render_char(char, font, text_color, bg_color, stroke_width, stroke_color, (shadow_x, shadow_y), shadow_color)
            if img: char_results.append({"char": char, "img": img, "meta": meta})
            elif meta: invisible_chars.append({"char": char, "meta": meta})
        
        # 预览网格
        cols = st.columns(8)
        for i, res in enumerate(char_results):
            with cols[i % 8]:
                st.markdown(f'<div class="char-card">', unsafe_allow_html=True)
                # 为预览添加网格背景
                st.markdown('<div class="preview-bg">', unsafe_allow_html=True)
                st.image(res['img'], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.caption(f"'{res['char']}'")
                st.markdown(f'</div>', unsafe_allow_html=True)
        
        atlas_img, fnt_content = None, ""
        if export_atlas and char_results:
            atlas_img, packed_chars = create_atlas(char_results, padding=2, force_pow2=force_pow2)
            # 合并不可见字符的 meta 用于 fnt
            all_meta_for_fnt = packed_chars + [{"atlas_x":0, "atlas_y":0, "meta": c['meta']} for c in invisible_chars]
            
            # 修复：获取正确的字体名称
            font_name = uploaded_font.name if uploaded_font else os.path.basename(DEFAULT_FONT_PATH)
            fnt_content = generate_fnt_text(font_name, font_size, atlas_img.width, atlas_img.height, all_meta_for_fnt)
            with st.expander(t("atlas_preview"), expanded=False):
                st.markdown('<div class="preview-bg">', unsafe_allow_html=True)
                st.image(atlas_img, caption=t("atlas_caption"))
                st.markdown('</div>', unsafe_allow_html=True)
                st.code(fnt_content[:500] + "...", language="text")

        st.markdown("---")
        st.subheader(t("export_section"))
        if st.button(t("dl_all_btn")):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for res in char_results:
                    img_byte_arr = io.BytesIO()
                    res['img'].save(img_byte_arr, format='PNG')
                    zip_file.writestr(f"individual/char_{ord(res['char'])}.png", img_byte_arr.getvalue())
                if atlas_img:
                    atlas_byte_arr = io.BytesIO()
                    atlas_img.save(atlas_byte_arr, format='PNG')
                    zip_file.writestr("font.png", atlas_byte_arr.getvalue())
                    zip_file.writestr("font.fnt", fnt_content.encode('utf-8'))
            st.download_button(label=t("dl_link_text"), data=zip_buffer.getvalue(), file_name="bitmap_fonts_pack.zip", mime="application/zip")
            
    except Exception as e:
        st.error(f"{t('error_prefix')} {str(e)}")
        st.exception(e)
else:
    st.info(t("info_msg"))

# 页面底部完成
