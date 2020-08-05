
# This script is for loading the add-on via the text editor.
# This is to make debugging easier without having to restart Blender every time a change is made.

import os
import sys
import bpy

MODULE_NAMES = [
  "fs_helpers",
  "dzb",
  "dzb_constants",
  "import_dzb",
  "export_dzb",
]

addon_dir = os.path.dirname(bpy.context.space_data.text.filepath)

init_file_name = "__init__.py"

if addon_dir not in sys.path:
  sys.path.append(addon_dir)

init_file_path = os.path.join(addon_dir, init_file_name)

# Reload any of the custom modules that were already loaded.
# This is so changes since the last test run take effect without needing to reload Blender.
import importlib
for module_name in MODULE_NAMES:
  if module_name in sys.modules:
    importlib.reload(sys.modules[module_name])

# Initialize the add-on.
exec(compile(open(init_file_path).read(), init_file_name, "exec"))
