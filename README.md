
## About

This is a Blender add-on for editing DZB collision models.  
The DZB format is used by The Legend of Zelda: The Wind Waker for all map collision as well as some object collision. It's also used by The Legend of Zelda: Twilight Princess for some objects but not for any maps.  

This add-on only supports Blender 2.80 or higher. Blender 2.79 will not work.  

## Installation

* Download the add-on from this link: https://github.com/LagoLunatic/blender_dzb_tools/archive/master.zip
* Extract the zip file you downloaded.
* Copy the `dzb_tools` folder into `%APPDATA%\Blender Foundation\Blender\2.83\scripts\addons`. (Replace the 2.83 in the path with whatever Blender version you're using, e.g. 2.80, 2.82, etc.)
* In Blender, go to Edit -> Preferences -> Add-ons. Search for "DZB" and enable "Import-Export: DZB Tools".
* Blender will now have options for DZB Collision added to its import and export menus.

## Usage

### Importing and exporting

Before you can import a DZB model, you'll need to extract the .dzb file from the RARC archive it's in.  
I recommend using [GCFT](https://github.com/LagoLunatic/GCFT) to extract RARC archives.  

For example, if you wanted to import Outset Island's collision into Blender, you would first open `files/res/Stage/sea/Room44.arc` in GCFT, right click on `room.dzb` and choose Extract File.  
Then in Blender, go to File -> Import -> DZB Collision and select `room.dzb`.  

Once you've finished editing the collision model, go to File -> Export -> DZB Collision to export a new .dzb file.  
Then back in GCFT, right click on `room.dzb` and choose Replace File, selecting your new .dzb file.  
Export the RARC archive, overwriting `Room44.arc`, and when you go to Outset Island ingame it should have your modified collision.  

### Viewing collision in Blender

When you first open a DZB file in Blender, you might not be able to see anything. This is because Wind Waker's maps are extremely large in scale compared to what Blender expects by default, so Blender cuts off geometry that is far away from your view.  
To fix this, first press N to bring up the right sidebar. Then switch to the "View" tab. Change "Clip Start" to 25 meters and "End" to 200000 meters.  
Depending on the size of the map you're editing you may want to adjust those numbers higher or lower.  

### Editing collision properties

DZB collision has custom properties that determine how the collision behaves. Is it solid or water, what sound do footsteps make on it, can the player climb up it, etc.  

There are two different type of DZB custom properties, and each is found in a different place in Blender.  
The first type is tied to each mesh object. These can be found in the Object Properties tab, by scrolling to the bottom of it and expanding "Custom Properties". You should see properties including is_lava, is_water, and rtbl_index here.  
The second type is tied to individual faces within a mesh. These are handled by having a material hold the properties, so they can be found in the Material properties tab, by scrolling to the bottom of it and expanding "Custom Properties". You should see properties including attribute_type, exit_index, and sound_id here.  

Note that because the second type of property is held by a material, if you edit a property on a material for one face, all other faces in the whole model with those same properties will be affected because they share the same material.  
You may want that, but if you don't, and only want to change a property for a few specific faces, you will first need to make a copy of the material they have so that it's separated from the material the other faces use.  
This can be done like so:  
1. Select one of the faces you want to edit the properties of in edit mode.
2. Take note of which material that face has (e.g. "PropertyInfoSet-0040") in the Material Properties tab, this is the material you want to copy from.
3. Press the + button in the upper right corner of that tab to add a new material slot.
4. Below the materials list, there should be a button with a checkered sphere icon and a down arrow inside it. Click this button, and select the material you want to copy from (e.g. "PropertyInfoSet-0040"). This will put that material in the new slot, but does not make a copy yet.
5. Exit edit mode, and click the number button to the left of the shield icon. This will make a copy of the material, and will change the name to something like "PropertyInfoSet-0040.001".
6. You can now assign this new material to the faces you wanted to edit, and change its custom properties freely without worrying about the original material being modified.

![dzb copy material guide](https://i.imgur.com/J5eB1MD.png)
