
import os
import sys

if __name__ not in ["__main__", "__init__"]:
  addon_dir = os.path.dirname(__file__)
  assert os.path.isdir(addon_dir)
  if addon_dir not in sys.path:
    sys.path.append(addon_dir)

import import_dzb
import export_dzb
from dzb_constants import GROUP_ATTRIBUTE_BOOLS, GROUP_ATTRIBUTE_INTS, GROUP_ATTRIBUTE_FLOATS
from dzb_constants import PROPERTY_ATTRIBUTE_INTS, PROPERTY_ATTRIBUTE_ENUMS

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

def register_custom_properties():
  # Register custom object/material properties.
  # TODO: A less hacky way of doing this is to make subclasses and register the custom properties on the subclasses, instead of the base Blender classes shared by everything.
  
  for attr_name in GROUP_ATTRIBUTE_BOOLS:
    bool_property = bpy.props.BoolProperty(
      name=attr_name,
    )
    setattr(bpy.types.Object, attr_name, bool_property)
  
  for attr_name, (min, max) in GROUP_ATTRIBUTE_INTS.items():
    int_property = bpy.props.IntProperty(
      name=attr_name,
      min=min,
      max=max,
    )
    setattr(bpy.types.Object, attr_name, int_property)
  
  for attr_name in GROUP_ATTRIBUTE_FLOATS:
    float_property = bpy.props.FloatProperty(
      name=attr_name,
    )
    setattr(bpy.types.Object, attr_name, float_property)
  
  for attr_name, (min, max) in PROPERTY_ATTRIBUTE_INTS.items():
    int_property = bpy.props.IntProperty(
      name=attr_name,
      min=min,
      max=max,
    )
    setattr(bpy.types.Material, attr_name, int_property)
  
  for attr_name, enum_values in PROPERTY_ATTRIBUTE_ENUMS.items():
    enum_value_items = []
    for enum_name, enum_value in enum_values.items():
      enum_value_items.append((enum_name, enum_name.replace("_", " "), "", "NONE", enum_value))
    
    enum_property = bpy.props.EnumProperty(
      name=attr_name,
      items=enum_value_items,
      default=enum_value_items[0][0],
    )
    setattr(bpy.types.Material, attr_name, enum_property)

def unregister_custom_properties():
  for attr_name in GROUP_ATTRIBUTE_BOOLS:
    delattr(bpy.types.Object, attr_name)
  
  for attr_name, (min, max) in GROUP_ATTRIBUTE_INTS.items():
    delattr(bpy.types.Object, attr_name)
  
  for attr_name in GROUP_ATTRIBUTE_FLOATS:
    delattr(bpy.types.Object, attr_name)
  
  for attr_name, (min, max) in PROPERTY_ATTRIBUTE_INTS.items():
    delattr(bpy.types.Material, attr_name)
  
  for attr_name, enum_values in PROPERTY_ATTRIBUTE_ENUMS.items():
    delattr(bpy.types.Material, attr_name)

def register():
  bpy.utils.register_class(ImportDZB)
  bpy.utils.register_class(ExportDZB)
  bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
  bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
  register_custom_properties()

def unregister():
  bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
  bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
  bpy.utils.unregister_class(ImportDZB)
  bpy.utils.unregister_class(ExportDZB)
  unregister_custom_properties()

if __name__ in ["__main__", "__init__"]:
  register()
