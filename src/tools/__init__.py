import os
import pkgutil
import importlib
import inspect

# 获取当前文件夹路径
package_path = os.path.dirname(__file__)
__all__ = []

# 获取当前包的名称 (例如 "src.tools")
current_package_name = __package__

# 只有在初次加载时才打印 Log，防止热重载刷屏
if 'has_initialized' not in globals():
    print(f"🔄 Initializing Tools from: {package_path} (Package: {current_package_name})")
    globals()['has_initialized'] = True

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
                # 3. 动态导入
                full_import_name = f"{current_package_name}.{category_name}.{module_name}"
                module = importlib.import_module(full_import_name)

                # 4. 提取函数
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and obj.__module__ == full_import_name and not name.startswith('_'):
                        
                        # 优化冲突检测逻辑：忽略同源模块的覆盖（即忽略热重载）
                        if name in globals():
                            old_obj = globals()[name]
                            if getattr(old_obj, '__module__', '') != obj.__module__:
                                print(f"  [⚠️ Warning] Tool conflict: '{name}' (from {old_obj.__module__}) is being overwritten by {name} (from {obj.__module__})!")
                        
                        # 挂载到当前命名空间
                        globals()[name] = obj
                        __all__.append(name)

            except Exception as e:
                print(f"    ❌ Error loading {category_name}/{module_name}: {e}")

# 同样，只在数量变化时或调试时打印
print(f"✨ Total tools loaded: {len(__all__)}")