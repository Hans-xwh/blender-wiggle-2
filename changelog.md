# Changelog


## 1.1.0 - (2026/07/11)
### Bone Pinning
* Reimplemented bone pinning system to be independent from Blender constraints. 
* Fixed a bug allowing `wiggle_reset()` to run in on invalid context. 
* Fixed a bug that could cause the simulation to crash when a bone had zero scale. 
* Fixed collisions being calculated on an invalid context (edit mode). 


## 1.0.2 - (2026/06/23)
* Fixed `Bake Wiggle` and `Select Enabled` on Blender 4.5 LTS. 
* Optimization: Removed an unnecessary View Layer update in `wiggle_pre()`. 


## 1.0.1 - (2026/06/06)
### Bone Sync  
* Added back sync functionality as an optional toggleable feature. 


## 1.0.0 - (2026/05/29)
### Revamp Update (Initial Release)  
* Changed file structure to be a proper extension. 
* Migrated properties into Property Groups. 
* Fixed display of the collision settings UI. 
* Restored preroll functionality when baking wiggle into keyframes. 
* Added an operator to clean up properties left by older versions of Wiggle 2. 
