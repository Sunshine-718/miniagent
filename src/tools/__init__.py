import os
import sys  # <--- 新增: 需要用到 sys.modules
import pkgutil
import importlib
import inspect

# 获取当前文件夹路径
package_path = os.path.dirname(__file__)
__all__ = []

# 获取当前包的名称 (例如 "src.tools")
current_package_name = __package__

# 标记初始化状态，避免首次启动刷屏，但在 Reload 时允许打印
if 'has_initialized' not in globals():
    print(f"🔄 Initializing Tools from: {package_path} (Package: {current_package_name})")
    globals()['has_initialized'] = True
else:
    print(f"🔄 Reloading Tools... (Detecting changes in {package_path})")

# 1. 扫描子文件夹
for entry in os.scandir(package_path):
    if entry.is_dir() and not entry.name.startswith('_') and not entry.name.startswith('.'):
        category_name = entry.name
        category_path = entry.path
        
        # 2. 扫描子文件夹内的 .py 文件
        for _, module_name, _ in pkgutil.iter_modules([category_path]):
            if module_name.startswith('_'): 
                continue

            try:
                # 3. 构造完整包路径
                full_import_name = f"{current_package_name}.{category_name}.{module_name}"

                # =========================================================
                # 🔥 核心修复：强制级联重载 (Deep Reload)
                # =========================================================
                if full_import_name in sys.modules:
                    # 如果模块已经在内存里，说明是热重载，必须强制 reload 子模块
                    module = importlib.reload(sys.modules[full_import_name])
                else:
                    # 如果是第一次加载
                    module = importlib.import_module(full_import_name)
                # =========================================================

                # 4. 提取函数并注册
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and obj.__module__ == full_import_name and not name.startswith('_'):
                        
                        # 冲突检测（仅在非重载引发的覆盖时警告，减少误报）
                        if name in globals():
                            old_obj_value = globals()[name]
                            # 只有当模块路径真正不同时才报警
                            if getattr(old_obj_value, '__module__', '') != obj.__module__:
                                print(f"  [⚠️ Warning] Conflict: {name} ({old_obj_value.__module__}) -> ({obj.__module__})")
                        
                        # 挂载到当前命名空间
                        globals()[name] = obj
                        __all__.append(name)

            except Exception as e:
                print(f"    ❌ Error loading {category_name}/{module_name}: {e}")

print(f"✨ Total tools loaded: {len(__all__)}")

# 清理可能残留的非工具全局变量
for var_name in list(globals().keys()):
    if var_name not in __all__ and not var_name.startswith('_') and var_name not in ['has_initialized']:
        # 检查是否为函数，如果不是函数则可能是残留变量
        if not callable(globals().get(var_name)):
            del globals()[var_name]
        # 如果是函数但不在 __all__ 中，也可能是旧工具残留
        elif var_name not in __all__ and var_name not in ['print', 'os', 'sys', 'pkgutil', 'importlib', 'inspect']:
            # 特别清理已知的残留工具名
            if var_name.endswith('_test') or var_name == 'old_obj' or var_name == 'old_obj_value':
                del globals()[var_name]
                print(f"  [清理] 移除残留变量: {var_name}")