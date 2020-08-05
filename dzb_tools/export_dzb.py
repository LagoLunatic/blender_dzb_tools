
import bpy
import math
import os
import sys
from io import BytesIO
import colorsys

from fs_helpers import *
from dzb import DZB
from dzb_constants import GROUP_ATTRIBUTE_NAMES, PROPERTY_ATTRIBUTE_NAMES

# TODO: what happens if the blender model has n-gons or quads?

def save(out_file_path):
  dzb = DZB()
  
  properties_by_material = {}
  for material in bpy.data.materials:
    property = dzb.add_property()
    
    for attr_name in PROPERTY_ATTRIBUTE_NAMES:
      prop_val = material[attr_name]
      setattr(property, attr_name, prop_val)
    
    properties_by_material[material] = property

  objects_in_hierarchy_order = []
  def loop_objects_recursive(parent_object):
    for child_object in parent_object.children:
      objects_in_hierarchy_order.append(child_object)
    for child_object in parent_object.children:
      loop_objects_recursive(child_object)
  root_object = next(obj for obj in bpy.data.objects if obj.parent is None)
  objects_in_hierarchy_order.append(root_object)
  loop_objects_recursive(root_object)

  object_to_group = {}
  for object in objects_in_hierarchy_order:
    if object.type not in ["MESH", "EMPTY"]:
      continue
    
    # TODO: remove the the number at the end of duplicate names (e.g. for outset, mizuba.001 -> mizuba)
    group_name = object.name
    group = dzb.add_group(group_name)
    object_to_group[object] = group
    
    if object.parent is None:
      group.parent_group = None
    else:
      group.parent_group = object_to_group[object.parent]
      group.parent_group.children.append(group)
    
    for attr_name in GROUP_ATTRIBUTE_NAMES:
      prop_val = object[attr_name]
      setattr(group, attr_name, prop_val)
    
    # Extract the transformation (commented out because it's unused by the game).
    #group.x_translation = object.location.x
    #group.y_translation = object.location.y
    #group.z_translation = object.location.z
    #group.x_rot = int(math.degrees(object.rotation_euler.x) * 0x4000 / 90) % 0x10000
    #group.y_rot = int(math.degrees(object.rotation_euler.y) * 0x4000 / 90) % 0x10000
    #group.z_rot = int(math.degrees(object.rotation_euler.z) * 0x4000 / 90) % 0x10000
    #group.x_scale = object.scale.x
    #group.y_scale = object.scale.y
    #group.z_scale = object.scale.z
    
    if object.type == "MESH":
      mesh = object.data
      
      properties_for_group = []
      for material in mesh.materials:
        property = properties_by_material[material]
        properties_for_group.append(property)
      
      for polygon in mesh.polygons:
        assert len(polygon.vertices) == 3
        
        vertices = []
        for vertex_index in polygon.vertices:
          vertex = tuple(mesh.vertices[vertex_index].co)
          vertices.append(vertex)
        
        property = properties_for_group[polygon.material_index]
        
        face = dzb.add_face(vertices, property, group)
  
  dzb.save_changes()
  #out_file_path = os.path.join(blend_file_directory, "room_out.dzb")
  with open(out_file_path, "wb") as f:
    f.write(read_all_bytes(dzb.data))
