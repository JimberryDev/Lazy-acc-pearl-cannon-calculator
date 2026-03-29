Hey!
I want to make a post on Lazy-chunk-weaponry in case an archiver likes it and wants to help with the wording
Here it is:

# 360 Lazy Acceleration Pearl Cannon
## Features
- Expandible memory (ROM) with up to 60 locations  (but it would be easy to make it bigger if you really need it to be)
- Block precision with an error of max ~15 blocks if you build right on top of the nether roof.
- Max range of ~100 000 blocks if you build on the nether roof. Which is 800 000 blocks on the overworld
- It comes with a calculator that generates schematics to input the locations to the ROM
- The calculator comes with a nice GUI, or you can download the scripts directly from Github
    - I tried to make the calculating part of the script as readable and clean so you can learn from it if you want, and maybe use it for your own cannon.
    - On the other hand, the gui was put together quickly and not worth learning from.
- It comes in two versions:
    - *Pretty:* Color coded. If you want to learn from it, this is the one to go for. It uses stained glass, concrete and terracotta.
    - *Cheap:* Stonebricks and stonebrick slabs. You can replace the stonebricks with any conductive block, and the slabs with any other type of slab or glass.


## Usage
### Building
1. Place the nether side schematic chunk aligned so the trapdoors with the lava underneath are in a chunk intersection, each in its own chunk
1. Take the coordinate where you are placing the schematic, and convert it to overworld coordinates by multiplying the X and Z by 8, but not the Y
1. Place the overworld side schematic exactly in those locations. It will most likely break if you don't
1. Build the nether portals first and check that you are in the correct positions:
    - The nether entrance portal should teleport you to the overword entrance portal, but not the other way around.
    - The chunk loaders should lead to each other perfectly.
    - The overworld portal that throws items to send signals should lead you to the nether version perfectly, independently on where you are when you use it
    - The nether portal that recieves items to recieve signals should lead to the overworld version if you stand next to the dropper when teleporting
1. Build the rest of the cannon except for the rom and tnt blocks
    - You can build the rom if you want, but it's not necesary until you add locations
1. Use the schematic verifier and only then place the tnt

### Adding targets
1. Run the calculator
1. Add the coordinates of the nether side schematic to the top
    - These get stored in a json file next to the calculator and loaded the next time you use the program.
    - You can safely delete this json if you want.
1. Add the amount of targets already present.
    - This will make sure to encode them in the next available spaces without overwriting the previous locations
    - This gets updated when you use the calculator and also stored into the json file
1. Add your coordinates and press "make schematic"
    - If you are using overworld coordinates, press the check box saying "overworld coordinates" and they will be automatically converted.
1. Select the location of your schematic and name
1. Before building the schematic, you want to pull the lever on a lamp with a sign. This will disconnect it as to not launch by accident
1. Place the schematic into minecraft in the next available spaces in the ROM and build
1. Press the reset button to clear the counters and unpull the lever from before.
1. On the overworld side, add the target to a lectern. 
    - If it is a target between 1 and 15, use the right-most lectern, between 17 and 31, the second right-most and so on.
    - The id of the page should match the id that the app tells you.
    - The id of each page on a lectern is its page number + 16 * (the amount of lecterns to the right of it)

### Traveling
1. Go to the overworld side
1. Align yourself in the corner marked with magenta glazed terracotta
1. Throw the enderpearl
1. Select in a lectern your location
1. Press the button ontop of that lectern
1. Wait until you get teleported and DO NOT load the nether side


## Credits
### Author
- JimberryDev
- [Follow me on Youtube](https://www.youtube.com/@JimberryDev)

### Used designs made by other people and link to where I got them from
- *Timing based binary decoder* by **@dzreams** from the [Storage Tech archive](https://discord.com/channels/748542142347083868/749136933191549028/997241072164016149) on Discord
- *Hopperspeed Hex to Binary Converter* by **@Andrews54757** from the [Storage Tech archive](https://discord.com/channels/748542142347083868/749136933191549028/939047254935896084) on Discord
- *4gt Nimply gate* by **b1nary** from the [Computational Minecraft archive](https://discord.com/channels/959155788092424253/959157573049786458/1016390683478720634) on Discord
- *Binary Counter* by **@Crain** from the [Computational Minecraft archive](https://discord.com/channels/959155788092424253/959157573049786458/1016384723578273832) on Discord
- *50 tnt compressor* originally by **@intricate, @enbyd (she | they), @Emir, @DatNerd, @Savva, @Rozbiynik** from a customizable lazy stab grid cannon on the [TNT Archive](https://discord.com/channels/809607812312858684/1218316302784008233/1218316302784008233)
- *Pearl aligner for 1.21.2+* by *@bread*, **[GaRLic BrEd1](https://www.youtube.com/@GaRLicBrEd1)**, from the [TNT Archive](https://discord.com/channels/809607812312858684/1342918454465794141/1342918454465794141) on Discord

### Inspiration

When making this, I took severe inspiration in the *360 Lazy Accel Ender Pearl Cannon* from **[WhiteMC](https://discord.com/channels/809607812312858684/1432514233886572687/1432514233886572687)** on the [TNT Archive](https://youtu.be/y9iA3AAPDNs). I ended up remaking most of it, but I would not have been able to do it without first learning how he did his version.


## Download
Get the latest version of the schematic and calculator [from here](https://github.com/JimberryDev/Lazy-acc-pearl-cannon-calculator/releases), on my github repository. There you can find releases for the cheap and pretty versions.

## Note
If you have any questions, feel free to ping me :)