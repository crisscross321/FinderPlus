# FinderPlus

macOS Finder 右键扩展 — 为 Finder 的右键菜单增加实用功能。

## 功能

安装后在 Finder 右键菜单中会新增以下选项：

| 菜单项 | 功能 |
|---|---|
| **新建文本文件** | 在当前目录创建空白 `.txt` 文件，自动编号去重 |
| **新建 Markdown** | 在当前目录创建空白 `.md` 文件，自动编号去重 |
| **新建文件夹** | 在当前目录创建子文件夹，自动编号去重 |
| **在此打开终端** | 在当前目录打开 Terminal |

## 安装

```bash
python3 install.py
```

安装完成后**重启 Finder**（或重新登录）使右键菜单生效：

```bash
killall Finder
```

## 使用

在 Finder 中**右键点击任意文件或文件夹**，右键菜单底部（「快捷操作」区域）即可看到新增选项：

- 选中**文件夹**右键 → 在该文件夹内执行操作
- 选中**文件**右键 → 在该文件的父目录内执行操作
- 未选中任何内容时 → 自动获取当前 Finder 窗口路径

## 卸载

```bash
rm -rf ~/Library/Services/{新建文本文件,新建\ Markdown,新建文件夹,在此打开终端}.workflow
```

## 原理

通过 Automator Quick Action 工作流实现。安装脚本在 `~/Library/Services/` 下生成 4 个 `.workflow` 包，每个包内含一个 Run Shell Script 动作，负责获取目标目录并执行对应操作。

## 许可

MIT
