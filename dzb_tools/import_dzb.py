
import bpy
import math
from io import BytesIO
import colorsys

from .dzb import DZB

from .dzb_constants import GROUP_ATTRIBUTE_NAMES, GROUP_ATTRIBUTE_BOOLS, GROUP_ATTRIBUTE_INTS
from .dzb_constants import PROPERTY_ATTRIBUTE_NAMES, PROPERTY_ATTRIBUTE_INTS, PROPERTY_ATTRIBUTE_ENUMS

OCTREE_DEBUG = False

# TODO: maybe move these enum things to the register function.
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

def read(in_file_path):
  with open(in_file_path, "rb") as f:
    data = BytesIO(f.read())
  dzb = DZB()
  dzb.read(data)
  
  
  if OCTREE_DEBUG:
    materials_by_block_index = []
    for block_index, block in enumerate(dzb.octree_blocks):
      material = bpy.data.materials.new("OctreeBlock-%04X" % block_index)
      
      # Procedurally generate a color for this material depending on the block index.
      # This attempts to make properties that are close together have noticeably different (and seemingly random) colors.
      h_offset  = (block_index % 8) / 8.0
      sv_offset = ((block_index // 8) % 4) / 4.0
      h = h_offset
      s = 1.0 - (sv_offset * 0.6)
      v = 0.4 + (sv_offset * 0.6)
      rgb = colorsys.hsv_to_rgb(h, s, v)
      
      alpha = 1.0
      
      material.diffuse_color = (rgb[0], rgb[1], rgb[2], alpha)
      
      materials_by_block_index.append(material)
  else:
    materials_by_property_index = []
    for property_index, property in enumerate(dzb.properties):
      material = bpy.data.materials.new("PropertyInfoSet-%04X" % property_index)
      
      # Procedurally generate a color for this material depending on the property index.
      # This attempts to make properties that are close together have noticeably different (and seemingly random) colors.
      h_offset  = (property_index % 8) / 8.0
      sv_offset = ((property_index // 8) % 4) / 4.0
      h = h_offset
      s = 1.0 - (sv_offset * 0.6)
      v = 0.4 + (sv_offset * 0.6)
      rgb = colorsys.hsv_to_rgb(h, s, v)
      
      alpha = 1.0
      if property.sound_id in [19, 20]: # TODO: check out 24, 23 as well
        # If the property has a water sound effect, make it partially transparent.
        # (Unfortunately whether it is actually water or not is determined by the group, so we can't determine it at the material level without using a hack like this.)
        alpha = 0.5
      
      material.diffuse_color = (rgb[0], rgb[1], rgb[2], alpha)
      #color = DISTINGUISHABLE_COLORS[property_index % len(DISTINGUISHABLE_COLORS)]
      
      # Assign property attributes to custom properties on the blender material.
      for attr_name in PROPERTY_ATTRIBUTE_NAMES:
        prop_val = getattr(property, attr_name)
        
        if attr_name in PROPERTY_ATTRIBUTE_INTS:
          max = PROPERTY_ATTRIBUTE_INTS[attr_name][1]
          if prop_val == max+1:
            # This is so things like exit index (which really ranges from 0-63) is instead displayed as -1 when at max value to represent null.
            prop_val = -1
        
        material[attr_name] = prop_val
      
      materials_by_property_index.append(material)
  
  
  
  objects_by_group_index = []
  for group_index, group in enumerate(dzb.groups):
    #print(group.name)
    dzb_faces = [
      f for f in dzb.faces
      if f.group_index == group_index
    ]
    
    dzb_vertices_for_group = []
    vertices = []
    faces = []
    materials_for_group = []
    for dzb_face in dzb_faces:
      for dzb_vertex in dzb_face.vertices:
        if dzb_vertex not in dzb_vertices_for_group:
          dzb_vertices_for_group.append(dzb_vertex)
          vertices.append((dzb_vertex.x_pos, dzb_vertex.y_pos, dzb_vertex.z_pos))
      
      face = tuple([
        dzb_vertices_for_group.index(dzb_vertex)
        for dzb_vertex in dzb_face.vertices
      ])
      faces.append(face)
      
      if OCTREE_DEBUG:
        for block_index, block in enumerate(dzb.octree_blocks):
          if dzb_face in block.faces:
            material = materials_by_block_index[block_index]
            break
      else:
        material = materials_by_property_index[dzb_face.property_index]
      if material not in materials_for_group:
        materials_for_group.append(material)
    
    edges = []
    
    if faces or vertices:
      mesh = bpy.data.meshes.new(group.name + "_mesh")
      mesh.from_pydata(vertices, edges, faces)
    else:
      mesh = None
    
    object = bpy.data.objects.new(group.name, mesh)
    
    if mesh:
      # Add properties as materials.
      for material in materials_for_group:
        object.data.materials.append(material)
      
      for face_index, polygon in enumerate(mesh.polygons):
        dzb_face = dzb_faces[face_index]
        if OCTREE_DEBUG:
          for block_index, block in enumerate(dzb.octree_blocks):
            if dzb_face in block.faces:
              material = materials_by_block_index[block_index]
              break
        else:
          material = materials_by_property_index[dzb_face.property_index]
        polygon.material_index = materials_for_group.index(material)
    
    # Assign group attributes to custom properties on the blender object.
    for attr_name in GROUP_ATTRIBUTE_NAMES:
      prop_val = getattr(group, attr_name)
      object[attr_name] = prop_val
    
    # Add the transformation (commented out because it's unused by the game).
    #object.rotation_mode = "ZYX"
    #object.location.x = group.x_translation
    #object.location.y = group.y_translation
    #object.location.z = group.z_translation
    #object.rotation_euler.x = math.radians(float(group.x_rot) / 0x4000 * 90)
    #object.rotation_euler.y = math.radians(float(group.y_rot) / 0x4000 * 90)
    #object.rotation_euler.z = math.radians(float(group.z_rot) / 0x4000 * 90)
    #object.scale.x = group.x_scale
    #object.scale.y = group.y_scale
    #object.scale.z = group.z_scale
    
    bpy.context.collection.objects.link(object)
    
    if group.parent_group_index != -1:
      object.parent = objects_by_group_index[group.parent_group_index]
    
    objects_by_group_index.append(object)
  
  if objects_by_group_index:
    # Account for the Y-up/Z-up difference between the game and Blender.
    objects_by_group_index[0].rotation_euler = (math.radians(90), 0, 0)
