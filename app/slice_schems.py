import os
import sys
from pathlib import Path
from litemapy import Schematic, BlockState, Region
from cannon_calc import target_to_binary
from data_classes import EncodedTarget


BASE_DIR = Path(__file__).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
OUT_FOLDER = APP_DIR / "out"

DATA_SLICE = SRC_DIR / "Data slice.litematic"
DECODER_SLICE = SRC_DIR / "Decoder slice.litematic"
REPEATER = SRC_DIR / "Repeater.litematic"

AUTHOR = "JimberryDev"
# This is the latest id the memory can store. The actual amount of memory slots is different.
MAX_SCHEMATIC = 63


def coords_to_data_region(cannon, target) -> Region:
    """Make a region with the observers and rails in place to add to memory some target.

    Args:
        cannon (tupple[int x, int y, int z]): The position of the schematic
        target (tupple[int x, int y, int z]): The coordinate of your target

    Returns:
        Region: A region with the bits that encode the target tnt to get to target.
    """
    return bits_to_region(*target_to_binary(cannon, target))


def bits_to_region(b_x: str, b_z: str) -> Region:
    """Make a region with the observers in place to encode the given bits.

    Args:
        b_x (str): A string encoding the amount of tnt to be launched in the x axis.
        b_z (str): A string encoding the amount of tnt to be launched in the z axis.

    Returns:
        Region: A region with the bits that encode the bits in the correct place.
    """
    b_z = b_z.replace(" ", "")
    b_x = b_x.replace(" ", "")

    # Load schematic
    schem = Schematic.load(DATA_SLICE)

    # Assume first region
    region = normalize_region(next(iter(schem.regions.values())))

    for i, c in enumerate(b_z):
        if c == '1':
            region[i, -2, 0] = BlockState("minecraft:observer", facing="down")
    for i, c in enumerate(b_x):
        if c == '1':
            region[i, -4, 0] = BlockState("minecraft:observer", facing="up")

    return region


def save_data_schem(name, cannon, target) -> Schematic:
    """Make and save a schematic encoding the data needed to get from cannon to target

    Args:
        name (str): The name for the schematic
        cannon (tupple[int x, int y, int z]): The position of the schematic
        target (tupple[int x, int y, int z]): The coordinate of your target

    Returns:
        Schematic: The saved schematic
    """

    # Make and save schematic
    os.makedirs(OUT_FOLDER, exist_ok=True)
    region = coords_to_data_region(cannon, target)
    schem = region.as_schematic(name=name, author=AUTHOR)
    schem.save(f"{OUT_FOLDER}/{name}.litematic")
    return schem


def make_decoder_slice_region(n: int) -> Region:
    if not (0 < n <= MAX_SCHEMATIC):
        raise ValueError(f"The index must lie between 0 and {MAX_SCHEMATIC+1}")

    b = format(n, "06b")

    # Load schematic
    schem = Schematic.load(DECODER_SLICE)

    # Assume first region
    region: Region = normalize_region(next(iter(schem.regions.values())))

    for i, c in enumerate(b):
        if c == '0':
            region[i, 3, 0] = BlockState("minecraft:observer", facing="down")

    return region


def copy_region(region: Region, new_x, new_y, new_z) -> Region:
    """
    Create a copy of a region at a new schematic position.

    Keeps blocks, entities, tile entities, and ticks.
    """

    new_region = Region(new_x, new_y, new_z,
                        region.width, region.height, region.length)

    # Copy blocks (local coords → same local coords)
    for x, y, z in region.block_positions():  # type: ignore
        new_region[x, y, z] = region[x, y, z]

    # Copy metadata
    new_region.entities.extend(region.entities)
    new_region.tile_entities.extend(region.tile_entities)
    new_region.block_ticks.extend(region.block_ticks)
    new_region.fluid_ticks.extend(region.fluid_ticks)

    return new_region


def rom_slice_from_bits(id: int, b_x: str, b_z: str):
    """Returns a region for a schematic that contains the slice decoding the id and the slice encoding the tnts.

    Args:
        id (int): the id to be decoded
        b_x (str): A string with the binary encoding the tnt amounts on the X axis
        b_z (str): A string with the binary encoding the tnt amounts on the Z axis

    Returns:
        Region: The region with the blocks to decode the id and encode the tnt.
    """
    decoder = make_decoder_slice_region(id)
    data = bits_to_region(b_x, b_z)

    data = copy_region(
        data,
        decoder.width,
        0,0
    )

    slice = merge_regions([data, decoder])
    return slice


def rom_slice(id: int, cannon: tuple[int, int, int], target: tuple[int, int, int]) -> Region:
    """Returns a region for a schematic that contains the slice decoding the id and the slice encoding the tnts.

    Args:
        id (int): the id to be decoded
        cannon (tuple[int, int, int]): A tuple with the coordinates xyz of the cannon
        target (tuple[int, int, int]): A tuple with the coordinates xyz of the target

    Returns:
        Region: The region with the blocks to decode the id and encode the tnt.
    """

    b_x, b_z = target_to_binary(cannon, target)
    return rom_slice_from_bits(id, b_x, b_z)


def rom_entries(name: str, starting_id: int, encoded_targets: list[EncodedTarget]) -> Schematic:
    """Create a schematic with everything you need to add targets to the lazy acc cannon.
    It includes slices for the decoder as well encoding the tnt. 

    Args:
        name (str): The name of the schematic
        starting_id (int): The number of the first target
        encoded_targets (list[EncodedTarget]): A list with all of the targets to be added.

    Raises:
        ValueError: starting_id must be more than 0 and less than MAX_SCHEMATICS

    Returns:
        Schematic: A schematic with the decoder and encoder for your targets
    """

    repeater_s = Schematic.load(REPEATER)
    repeater = normalize_region(next(iter(repeater_s.regions.values())))

    slices = {}
    cur_z = 0
    id = starting_id
    for t in encoded_targets:
        if (id % 8 == 0):
            slices[f"repeater{id//8}"] = copy_region(repeater, repeater.x, repeater.y, cur_z)
            cur_z += 1

        if (id % 16 == 0):
            id += 1 # Skip multiples of 16 because of an interface limitation

        slice = rom_slice_from_bits(id, t.x_bits, t.z_bits)
        slice = copy_region(slice, slice.x, slice.y, cur_z)

        target_name = t.name or str(id)

        # How many regions are already present in slices with the name target_name
        existing_same_name = sum(1 for k in slices.keys() if k.startswith(t.name))
        if existing_same_name == 0:
            slices[target_name] = slice
        else:
            slices[f"{target_name}_{existing_same_name}"] = slice

        cur_z += 1
        id += 1

    schem = Schematic(name=name, author=AUTHOR, regions=slices)

    return schem


def merge_regions(regions, merged_x=None, merged_y=None, merged_z=None):
    """
    Merge multiple regions into a single new region.

    Parameters
    ----------
    regions : list[Region]
        Regions to merge.
    merged_x, merged_y, merged_z : int | None
        Optional origin of the merged region. If None, uses the minimum
        schematic coordinates across all regions.

    Returns
    -------
    Region
        A new region containing all input regions.

    Notes
    -----
    - If regions overlap, later regions overwrite earlier ones.
    - Assumes regions have positive dimensions.
    """

    if not regions:
        raise ValueError("No regions provided")

    # Compute bounding box across all regions
    min_x = min(r.min_schem_x() for r in regions)
    max_x = max(r.max_schem_x() for r in regions)
    min_y = min(r.min_schem_y() for r in regions)
    max_y = max(r.max_schem_y() for r in regions)
    min_z = min(r.min_schem_z() for r in regions)
    max_z = max(r.max_schem_z() for r in regions)

    # Default origin = minimum corner
    if merged_x is None:
        merged_x = min_x
    if merged_y is None:
        merged_y = min_y
    if merged_z is None:
        merged_z = min_z

    # Create merged region
    merged = Region(
        merged_x,
        merged_y,
        merged_z,
        max_x - min_x + 1,
        max_y - min_y + 1,
        max_z - min_z + 1,
    )

    # Copy all regions into merged
    for region in regions:
        for x, y, z in region.block_positions():
            schem_x = region.x + x
            schem_y = region.y + y
            schem_z = region.z + z

            merged_x_local = schem_x - merged.x
            merged_y_local = schem_y - merged.y
            merged_z_local = schem_z - merged.z

            merged[merged_x_local, merged_y_local, merged_z_local] = region[x, y, z]

        merged.entities.extend(region.entities)
        merged.tile_entities.extend(region.tile_entities)
        merged.block_ticks.extend(region.block_ticks)
        merged.fluid_ticks.extend(region.fluid_ticks)

    return merged


def normalize_region(region: Region) -> Region:
    """
    Return a copy of the region where local coordinates start at (0,0,0)
    and dimensions are positive.

    This removes negative coordinate ranges and makes indexing consistent.
    """

    # Determine local coordinate bounds
    min_x, max_x = region.min_x(), region.max_x()   # type: ignore
    min_y, max_y = region.min_y(), region.max_y()   # type: ignore
    min_z, max_z = region.min_z(), region.max_z()   # type: ignore

    width  = max_x - min_x + 1
    height = max_y - min_y + 1
    length = max_z - min_z + 1

    # Create new region starting at (0,0,0)
    new_region = Region(0, 0, 0, width, height, length)

    # Copy blocks
    for x, y, z in region.block_positions():    # type: ignore
        new_x = x - min_x
        new_y = y - min_y
        new_z = z - min_z

        new_region[new_x, new_y, new_z] = region[x, y, z]

    # Copy metadata
    new_region.entities.extend(region.entities)
    new_region.tile_entities.extend(region.tile_entities)
    new_region.block_ticks.extend(region.block_ticks)
    new_region.fluid_ticks.extend(region.fluid_ticks)

    return new_region


if __name__ == "__main__":
    if len(sys.argv) == 8:
        canon_x, canon_y, canon_z, target_x, target_y, target_z = map(int, sys.argv[1:7])
        name = sys.argv[7]

        rom_slice(1, (canon_x, canon_y, canon_z), (target_x, target_y, target_z))

        save_data_schem(name, (canon_x, canon_y, canon_z), (target_x, target_y, target_z))

    else:
        print(
            "Expected 3 arguments: the coords for the cannon origin "
            "(where you placed the schematic), the coords for the target and the name of the output schematic.\n"
            "Usage: python script.py x0 y0 z0 xt yt zt name\n"
            "Example: python script.py 0 137 0 10 128 -5 'witch farm'\n"
        )
