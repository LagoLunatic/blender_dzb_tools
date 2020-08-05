
import os
import sys

if __name__ not in ["__main__", "__init__"]:
  addon_dir = os.path.dirname(__file__)
  assert os.path.isdir(addon_dir)
  if addon_dir not in sys.path:
    sys.path.append(addon_dir)

import import_dzb
import export_dzb

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper

bl_info = {
  "name": "DZB Tools",
  "author": "LagoLunatic",
  "description": "Import/export tools for DZB collision model editing.",
  "version": (0, 1, 0),
  "blender": (2, 80, 0),
  "category": "Import-Export",
  "tracker_url": "https://github.com/LagoLunatic/blender_dzb_tools/issues",
}

class ImportDZB(Operator, ImportHelper):
  bl_idname = 'dzb_tools.import_dzb'
  bl_label = 'Import DZB Collision (.dzb)'
  bl_description = 'Load a Wind Waker DZB collision model.'
  bl_options = {'REGISTER', 'UNDO', 'PRESET'}
  
  filename_ext = '.dzb'
  filter_glob: bpy.props.StringProperty(default='*.dzb;', options={'HIDDEN'})
  
  def execute(self, context):
    if not self.filepath:
      raise Exception("No filepath set.")
    
    import_dzb.read(self.filepath)
    return {"FINISHED"} 

class ExportDZB(Operator, ExportHelper):
  bl_idname = 'dzb_tools.export_dzb'
  bl_label = 'Export DZB Collision (.dzb)'
  bl_description = 'Write a Wind Waker DZB collision model.'
  bl_options = {'REGISTER', 'UNDO', 'PRESET'}
  
  filename_ext = '.dzb'
  filter_glob: bpy.props.StringProperty(default='*.dzb;', options={'HIDDEN'})
  
  def execute(self, context):
    if not self.filepath:
      self.report({"ERROR"}, "No filepath set.")
      return
    
    export_dzb.save(self.filepath)
    return {"FINISHED"}

def menu_func_import(self, context):
  self.layout.operator(ImportDZB.bl_idname, text='DZB Collision (.dzb)', icon='NONE')

def menu_func_export(self, context):
  self.layout.operator(ExportDZB.bl_idname, text='DZB Collision (.dzb)', icon='NONE')

def register():
  bpy.utils.register_class(ImportDZB)
  bpy.utils.register_class(ExportDZB)
  bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
  bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
  bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
  bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
  bpy.utils.unregister_class(ImportDZB)
  bpy.utils.unregister_class(ExportDZB)

if __name__ in ["__main__", "__init__"]:
  register()
