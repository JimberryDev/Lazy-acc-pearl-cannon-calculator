from dataclasses import dataclass
import tkinter as tk

CoordinateEntries = tuple[tk.Entry, tk.Entry, tk.Entry]
ValidatorCommand = tuple[str, str]

@dataclass
class TargetRow:
    """Widgets associated with one target row."""

    frame: tk.Frame
    name_entry: tk.Entry
    coordinate_entries: CoordinateEntries
    remove_btn: tk.Button


@dataclass
class SavedState:
    """Persistent GUI state stored on disk."""

    origin_x: int
    origin_y: int
    origin_z: int
    starting_id: int


@dataclass
class Coordinates:
    """Three-dimensional integer coordinates."""

    x: int
    y: int
    z: int


@dataclass
class SchematicTarget:
    """One named target for schematic generation."""

    name: str
    x: int
    y: int
    z: int

@dataclass
class EncodedTarget:
    name: str
    x_bits: str
    z_bits: str