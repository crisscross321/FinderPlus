#!/usr/bin/env python3
"""
FinderPlus - macOS Finder 右键扩展
====================================
在 Finder 中右键点击文件/文件夹，菜单中会新增以下选项：
  ① 新建文本文件    → 创建空白 .txt
  ② 新建 Markdown   → 创建空白 .md
  ③ 新建文件夹      → 创建子文件夹
  ④ 在此打开终端    → 打开 Terminal 到当前目录

原理：在 ~/Library/Services/ 下创建 4 个 Automator Quick Action 工作流包。
"""

import os
import plistlib
import shutil
import subprocess
import sys
import uuid

SERVICES_DIR = os.path.expanduser("~/Library/Services")

# ── 通用脚本：获取目标目录 ──────────────────────────────────
# 优先使用用户选中的文件夹，其次是选中文件的父目录，
# 如果都没选中则用 AppleScript 获取最前面 Finder 窗口的路径，
# 最后一律回退到桌面。
GET_TARGET_DIR = r"""
TARGET=""
if [ $# -gt 0 ]; then
  if [ -d "$1" ]; then
    TARGET="$1"
  else
    TARGET="$(dirname "$1")"
  fi
else
  TARGET="$(osascript -e \
    'tell application "Finder" to if (count of windows) > 0 then POSIX path of (target of front window as alias)' \
    2>/dev/null)"
fi
if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
  TARGET="$HOME/Desktop"
fi
""".lstrip("\n")

# ── 四个服务定义 ────────────────────────────────────────────
SERVICES = [
    {
        "name": "新建文本文件",
        "bundle_id": "com.finderplus.new-text-file",
        "script": GET_TARGET_DIR.rstrip() + '\n\ncd "$TARGET" || exit 1\nN="未命名"; I=1\n'
                  'while [ -e "$N.txt" ]; do I=$((I + 1)); N="未命名 $I"; done\n'
                  'touch "$N.txt" && open -R "$N.txt"\n',
    },
    {
        "name": "新建 Markdown",
        "bundle_id": "com.finderplus.new-markdown",
        "script": GET_TARGET_DIR.rstrip() + '\n\ncd "$TARGET" || exit 1\nN="未命名"; I=1\n'
                  'while [ -e "$N.md" ]; do I=$((I + 1)); N="未命名 $I"; done\n'
                  'touch "$N.md" && open -R "$N.md"\n',
    },
    {
        "name": "新建文件夹",
        "bundle_id": "com.finderplus.new-folder",
        "script": GET_TARGET_DIR.rstrip() + '\n\ncd "$TARGET" || exit 1\nN="未命名文件夹"; I=1\n'
                  'while [ -d "$N" ]; do I=$((I + 1)); N="未命名文件夹 $I"; done\n'
                  'mkdir "$N" && open -R "$N"\n',
    },
    {
        "name": "在此打开终端",
        "bundle_id": "com.finderplus.open-terminal",
        "script": GET_TARGET_DIR.rstrip() + '\n\ncd "$TARGET" && open -a Terminal "$TARGET"\n',
    },
]


def make_workflow(service, wf_dir):
    """为一个服务生成完整的 .workflow 包。"""
    contents = os.path.join(wf_dir, "Contents")
    resources = os.path.join(contents, "Resources")
    os.makedirs(resources, exist_ok=True)

    # ── Info.plist ──
    info = {
        "CFBundleDevelopmentRegion": "en_US",
        "CFBundleIdentifier": service["bundle_id"],
        "CFBundleName": service["name"],
        "CFBundleShortVersionString": "1.0",
        "NSServices": [
            {
                "NSMenuItem": {"default": service["name"]},
                "NSMessage": "runWorkflowAsService",
                "NSSendFileTypes": ["public.folder"],
            }
        ],
    }
    with open(os.path.join(contents, "Info.plist"), "wb") as f:
        plistlib.dump(info, f)

    # ── document.wflow（位于 Contents/Resources/）──
    action_uuid = str(uuid.uuid4()).upper()
    input_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()

    document = {
        "AMApplicationBuild": "346",
        "AMApplicationVersion": "2.3",
        "AMDocumentVersion": "2",
        "actions": [
            {
                "action": {
                    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "CheckedForUserDefaultShell": True,
                        "COMMAND_STRING": service["script"],
                        "inputMethod": 1,
                        "shell": "/bin/zsh",
                        "source": "",
                    },
                    "AMAccepts": {
                        "Container": "List",
                        "Optional": True,
                        "Types": ["com.apple.cocoa.path"],
                    },
                    "AMActionVersion": "2.0.3",
                    "AMApplication": ["Automator"],
                    "AMParameterProperties": {
                        "CheckedForUserDefaultShell": {},
                        "COMMAND_STRING": {},
                        "inputMethod": {},
                        "shell": {},
                        "source": {},
                    },
                    "AMProvides": {
                        "Container": "List",
                        "Types": ["com.apple.cocoa.path"],
                    },
                    "arguments": {
                        "0": {
                            "default value": 0,
                            "name": "inputMethod",
                            "required": "0",
                            "type": "0",
                            "uuid": "0",
                        },
                        "1": {
                            "default value": "",
                            "name": "source",
                            "required": "0",
                            "type": "0",
                            "uuid": "1",
                        },
                        "2": {
                            "default value": 0,
                            "name": "CheckedForUserDefaultShell",
                            "required": "0",
                            "type": "0",
                            "uuid": "2",
                        },
                        "3": {
                            "default value": "",
                            "name": "COMMAND_STRING",
                            "required": "0",
                            "type": "0",
                            "uuid": "3",
                        },
                        "4": {
                            "default value": "/bin/zsh",
                            "name": "shell",
                            "required": "0",
                            "type": "0",
                            "uuid": "4",
                        },
                    },
                    "BundleIdentifier": "com.apple.RunShellScript",
                    "CanShowSelectedItemsWhenRun": True,
                    "CanShowWhenRun": True,
                    "Category": ["AMCategoryUtilities"],
                    "CFBundleVersion": "2.0.3",
                    "Class Name": "RunShellScriptAction",
                    "InputUUID": input_uuid,
                    "Keywords": ["Shell", "Script", "Files"],
                    "location": "309.500000:631.000000",
                    "nibPath": "/System/Library/Automator/Run Shell Script.action/Contents/Resources/en.lproj/main.nib",
                    "OutputUUID": output_uuid,
                    "UnlocalizedApplications": ["Automator"],
                    "UUID": action_uuid,
                },
                "isViewVisible": True,
            }
        ],
        "connectors": {},
        "workflowMetaData": {
            "serviceApplicationBundleID": "com.apple.finder",
            "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
            "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }
    with open(os.path.join(resources, "document.wflow"), "wb") as f:
        plistlib.dump(document, f)


def main():
    print("\n🔧 FinderPlus — macOS Finder 右键扩展安装器\n")

    # 检查 Python 版本
    if sys.version_info < (3, 6):
        sys.exit("❌ 需要 Python 3.6+，当前版本: " + sys.version)

    os.makedirs(SERVICES_DIR, exist_ok=True)

    # 安装每个服务
    for svc in SERVICES:
        wf_dir = os.path.join(SERVICES_DIR, svc["name"] + ".workflow")
        if os.path.exists(wf_dir):
            shutil.rmtree(wf_dir)
        try:
            make_workflow(svc, wf_dir)
            print(f"  ✅  {svc['name']}")
        except Exception as e:
            print(f"  ❌  {svc['name']} 安装失败: {e}")
            return 1

    print(f"\n📋 已安装 {len(SERVICES)} 个右键菜单选项：")
    for svc in SERVICES:
        print(f"   • {svc['name']}")

    print("\n💡 使用方法：在 Finder 中右键点击任意文件或文件夹，")
    print("   菜单底部会显示「快捷操作」或直接显示以上选项。")

    # 重启 Finder 以刷新服务注册
    try:
        resp = input("\n⚡ 是否现在重启 Finder? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        resp = ""
    if resp in ("y", "yes", "是"):
        subprocess.run(["killall", "Finder"], check=False)
        print("✅ Finder 已重启，现在可以右键试用了。")
    else:
        print("💡 你也可以稍后手动重启 Finder，或重新登录以使更改生效。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
