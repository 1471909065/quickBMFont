# quickBMFont

`quickBMFont` 是一个基于 Streamlit 的位图字体生成工具，支持上传字体文件、实时预览自定义字符、导出单字符 PNG 和 BMFont 纹理图集（`.fnt` + `font.png`）。适用于游戏开发、小程序、UI 字体资源制作等场景。
## 测试网站
https://urban-succotash-jqjjrj7jpwxfqx9j-8501.app.github.dev/#3bfae455

## 功能

- 多语言界面：中文与英文切换
- 上传 `.ttf` / `.otf` 字体文件
- 自定义字符输入并实时预览渲染结果
- 设置字体大小、文字颜色、背景类型（透明 / 纯色）
- 高级特效：描边、阴影
- 生成纹理图集（Atlas）与 BMFont 描述文件
- 一键打包下载：单字符 PNG、`font.png`、`font.fnt`

## 主要实现逻辑

- 使用 `Pillow` 渲染字符图像与效果
- 自动计算字符元数据并生成 BMFont 文本格式
- 生成可选的纹理图集并支持强制 2 的幂次方尺寸
- 通过 Streamlit 构建交互式 Web UI

## 依赖

- Python 3
- streamlit
- pillow

## 安装

```bash
pip install streamlit pillow
```

## 运行

```bash
streamlit run app.py
```

## 使用步骤

1. 打开应用后，在左侧上传 `.ttf` / `.otf` 字体文件。
2. 在文本输入框中输入要生成的字符。
3. 调整字体大小、颜色、背景、描边和阴影等样式。
4. 勾选“生成雪碧图 (Atlas + .fnt)”可生成纹理图集。
5. 点击“打包下载全部资源”下载 ZIP 文件。

## 注意事项

- 若未上传字体，应用会尝试使用代码中默认路径指定的字体文件。
- 生成的 BMFont 文件名默认为 `font.fnt`，对应的纹理文件名为 `font.png`。

## 文件结构

- `app.py`：Streamlit 应用主入口
- `README.md`：项目说明

## 版权与许可

本项目为个人演示工具，可根据需要修改和扩展。
