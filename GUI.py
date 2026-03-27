import json
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from slice_schems import MAX_SCHEMATICS, rom_entries
from data_classes import *


# ---- UI constants (layout & sizing) ----
ENTRY_WIDTH = 5
AXIS_LABEL_WIDTH = 2
LEFT_LABEL_WIDTH = 15
NAME_ENTRY_WIDTH = 18

UI_SCALE = 1.6

SECTION_PAD_X = 10
SECTION_PAD_Y = 10
COLUMN_GAP_X = 10
ROW_PAD_Y = 2
BUTTON_GAP_X = 10

WINDOW_MARGIN_X = 20
WINDOW_MARGIN_Y = 20

PLACEHOLDER_COLOR = "gray"
NORMAL_TEXT_COLOR = "black"

def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

SETTINGS_FILE = get_app_dir() / "lazy_acc_cannon_gui_state.json"


def only_int(proposed_value: str) -> bool:
    """Return True if the proposed entry value is a valid integer prefix.

    This allows:
    - an empty string, so the user can clear the field while editing
    - a leading minus sign for negative integers
    - digits
    """
    return proposed_value.lstrip("-") == "" or proposed_value.lstrip("-").isdigit()


def only_valid_id_int(proposed_value: str) -> bool:
    """Return True if the proposed entry value is a valid integer prefix.

    This allows:
    - an empty string, so the user can clear the field while editing
    - digits
    """
    return proposed_value == "" or (proposed_value.isdigit() and int(proposed_value) < MAX_SCHEMATICS)


def get_int(entry: tk.Entry, default: int = 0, *, allow_placeholder: bool = False) -> int:
    """Read an integer from an Entry widget.

    If the field is empty or invalid, return the provided default.
    Placeholder text is ignored by default, but it can be treated as a real
    value when allow_placeholder=True.
    """
    if is_placeholder_active(entry) and not allow_placeholder:
        return default

    try:
        return int(entry.get())
    except ValueError:
        return default


def bind_ctrl_backspace(entry: tk.Entry) -> None:
    """Add Ctrl+BackSpace behavior to delete the previous word.

    This mimics common OS/editor behavior for Entry widgets.
    """

    def on_ctrl_backspace(event):
        text = entry.get()
        i = entry.index(tk.INSERT)

        # Move left over any spaces
        while i > 0 and text[i-1].isspace():
            i -= 1

        # Move left over the word
        while i > 0 and not text[i-1].isspace():
            i -= 1

        entry.delete(i, tk.INSERT)
        return "break"

    entry.bind("<Control-BackSpace>", on_ctrl_backspace)


def add_placeholder(entry: tk.Entry, text: str) -> None:
    """Show gray placeholder text inside an Entry widget.

    Tkinter does not provide placeholder text natively, so this helper adds it.
    """
    entry._placeholder_text = text  # type: ignore[attr-defined]
    entry._placeholder_active = False  # type: ignore[attr-defined]

    def show_placeholder() -> None:
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg=PLACEHOLDER_COLOR)
            entry._placeholder_active = True  # type: ignore[attr-defined]

    def hide_placeholder() -> None:
        if is_placeholder_active(entry):
            entry.delete(0, tk.END)
            entry.config(fg=NORMAL_TEXT_COLOR)
            entry._placeholder_active = False  # type: ignore[attr-defined]

    def on_focus_in(_event) -> None:
        hide_placeholder()

    def on_focus_out(_event) -> None:
        show_placeholder()

    entry.bind("<FocusIn>", on_focus_in, add="+")
    entry.bind("<FocusOut>", on_focus_out, add="+")
    show_placeholder()


def is_placeholder_active(entry: tk.Entry) -> bool:
    """Return whether the entry is currently displaying placeholder text."""
    return bool(getattr(entry, "_placeholder_active", False))


def set_entry_text(entry: tk.Entry, text: str) -> None:
    """Replace the entry contents with normal, non-placeholder text."""
    entry.config(fg=NORMAL_TEXT_COLOR)
    entry.delete(0, tk.END)
    entry.insert(0, text)
    entry._placeholder_active = False  # type: ignore[attr-defined]


def load_saved_state() -> SavedState | None:
    """Load the saved GUI state from disk if it exists and is valid."""
    if not SETTINGS_FILE.exists():
        return None

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return SavedState(
            origin_x=int(data["origin_x"]),
            origin_y=int(data["origin_y"]),
            origin_z=int(data["origin_z"]),
            starting_id=int(data["starting_id"]),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def save_state(state: SavedState) -> None:
    """Save the GUI state to disk as JSON."""
    SETTINGS_FILE.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")


def make_xyz_fields(parent: tk.Misc, vcmd: ValidatorCommand) -> CoordinateEntries:
    """Create x, y, z integer fields inside an existing horizontal container."""
    x_entry = tk.Entry(parent, width=ENTRY_WIDTH, justify="right", validate="key", validatecommand=vcmd)
    x_entry.pack(side="left")
    tk.Label(parent, text="x", anchor="w", width=AXIS_LABEL_WIDTH).pack(side="left")

    y_entry = tk.Entry(parent, width=ENTRY_WIDTH, justify="right", validate="key", validatecommand=vcmd)
    y_entry.pack(side="left")
    tk.Label(parent, text="y", anchor="w", width=AXIS_LABEL_WIDTH).pack(side="left")

    z_entry = tk.Entry(parent, width=ENTRY_WIDTH, justify="right", validate="key", validatecommand=vcmd)
    z_entry.pack(side="left")
    tk.Label(parent, text="z", anchor="w", width=AXIS_LABEL_WIDTH).pack(side="left")

    return x_entry, y_entry, z_entry


def make_labeled_row(parent: tk.Misc, label_text: str) -> tuple[tk.Frame, tk.Frame]:
    """Create a row with a fixed-width right-aligned label and a content area.

    Returns the row frame and the content frame placed to the right of the label.
    """
    row = tk.Frame(parent)
    row.pack(anchor="center", pady=ROW_PAD_Y)

    tk.Label(row, text=label_text, anchor="e", width=LEFT_LABEL_WIDTH).pack(side="left", padx=(0, COLUMN_GAP_X))

    content_frame = tk.Frame(row)
    content_frame.pack(side="left")
    return row, content_frame


def make_targets_header_row(parent: tk.Misc, on_add_target: Callable[[], None]) -> None:
    """Create the row containing the Targets label and add button.

    This row is aligned with the full left edge of the other rows rather than
    starting at the coordinate-entry column.
    """
    row = tk.Frame(parent)
    row.pack(anchor="w", fill="x", pady=ROW_PAD_Y)

    tk.Label(row, text="Targets:").pack(side="left", padx=(0, BUTTON_GAP_X))
    tk.Button(row, text="+", command=on_add_target).pack(side="left")


def make_target_row(parent: tk.Misc, vcmd: ValidatorCommand) -> TargetRow:
    """Create one target row with name, coordinates, and action button.

    Target rows are aligned with the full left edge of the inputs section.
    """
    row = tk.Frame(parent)
    row.pack(anchor="w", fill="x", pady=ROW_PAD_Y)

    tk.Label(row, text="Name:").pack(side="left")

    name_entry = tk.Entry(row, width=NAME_ENTRY_WIDTH)
    name_entry.pack(side="left", padx=(0, AXIS_LABEL_WIDTH))
    bind_ctrl_backspace(name_entry)

    tk.Label(row, text=":").pack(side="left", padx=(0, AXIS_LABEL_WIDTH))

    coordinate_entries = make_xyz_fields(row, vcmd)
    add_placeholder(coordinate_entries[1], "128")

    # Overworld checkbox
    overworld_var = tk.BooleanVar(value=False)
    overworld_checkbox = tk.Checkbutton(row, text="Overworld coords", variable=overworld_var)
    overworld_checkbox.pack(side="left", padx=(BUTTON_GAP_X, 0))

    # store on row (no need to modify dataclass)
    row.overworld_var = overworld_var  # type: ignore

    remove_btn = tk.Button(row, text="-")
    remove_btn.pack(side="left", padx=(BUTTON_GAP_X, 0))

    return TargetRow(
        frame=row,
        name_entry=name_entry,
        coordinate_entries=coordinate_entries,
        remove_btn=remove_btn,
    )


def format_coordinates(entries: CoordinateEntries, *, allow_placeholder: bool = False) -> tuple[int, int, int]:
    """Convert a triple of Entry widgets into a triple of integers."""
    x_entry, y_entry, z_entry = entries
    return (
        get_int(x_entry, allow_placeholder=allow_placeholder),
        get_int(y_entry, allow_placeholder=allow_placeholder),
        get_int(z_entry, allow_placeholder=allow_placeholder),
    )


def get_target_name(entry: tk.Entry, default_index: int) -> str:
    """Return the target name or a generated fallback name."""
    name = entry.get().strip()
    return name or f"Target {default_index}"


def collect_targets(target_rows: list[TargetRow]) -> list[SchematicTarget]:
    """Read all target rows into plain data objects."""
    targets: list[SchematicTarget] = []

    for index, target_row in enumerate(target_rows, start=1):
        x, y, z = format_coordinates(target_row.coordinate_entries, allow_placeholder=True)

        # apply overworld conversion if needed
        if getattr(target_row, "overworld_var", None) and target_row.overworld_var.get():  # type: ignore
            x = x // 8
            z = z // 8

        targets.append(
            SchematicTarget(
                name=get_target_name(target_row.name_entry, index),
                x=x,
                y=y,
                z=z,
            )
        )

    return targets


def make_schematics(
    litematica_origin: Coordinates,
    targets: list[SchematicTarget],
    existing_targets_count: int,
    output_path: str,
) -> None:
    """Create the schematics for the current GUI inputs.

    Parameters
    ----------
    litematica_origin:
        Origin of the placed base schematic in the world.
    targets:
        All requested target rows from the GUI.
    existing_targets_count:
        Number of already existing schematics/IDs in the world.
    output_path:
        Destination .litematic file chosen by the user.

    This function is intentionally left empty for now and is the place where
    the actual schematic-generation code should go.
    """
    name = Path(output_path).stem
    schem = rom_entries(name=name, starting_id=existing_targets_count+1, cannon=litematica_origin, targets=targets)
    schem.save(output_path)


def main() -> None:
    """Create and run the GUI application."""
    root = tk.Tk()
    root.title("Coordinate Calculator")

    # Scale entire UI (fonts + widgets)
    root.tk.call("tk", "scaling", UI_SCALE)

    saved_state = load_saved_state()

    vcmd: ValidatorCommand = (root.register(only_int), "%P")
    id_vcmd: ValidatorCommand = (root.register(only_valid_id_int), "%P")

    # Keep the whole interface centered as the window grows.
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    main_frame = tk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="n")

    # Main vertical layout: inputs at the top, output text in the middle,
    # and action buttons at the bottom.
    inputs_frame = tk.Frame(main_frame, padx=SECTION_PAD_X, pady=SECTION_PAD_Y)
    inputs_frame.pack(anchor="center")

    text_frame = tk.Frame(main_frame, padx=SECTION_PAD_X, pady=SECTION_PAD_Y)
    text_frame.pack(anchor="center")

    buttons_frame = tk.Frame(main_frame, padx=SECTION_PAD_X, pady=SECTION_PAD_Y)
    buttons_frame.pack(anchor="center")

    rows_frame = tk.Frame(inputs_frame)
    rows_frame.pack(anchor="w")

    # First row: origin inputs.
    _, origin_content_frame = make_labeled_row(rows_frame, "Litematica origin:")
    origin_entries = make_xyz_fields(origin_content_frame, vcmd)

    if saved_state is not None:
        add_placeholder(origin_entries[0], str(saved_state.origin_x))
        add_placeholder(origin_entries[1], str(saved_state.origin_y))
        add_placeholder(origin_entries[2], str(saved_state.origin_z))
    else:
        add_placeholder(origin_entries[1], "128")

    # Index
    tk.Label(origin_content_frame, text="Number of existing targets:", anchor="w").pack(side="left")
    starting_id = tk.Entry(origin_content_frame, width=ENTRY_WIDTH, justify="right", validate="key", validatecommand=id_vcmd)
    starting_id.pack(side="left")

    if saved_state is not None:
        add_placeholder(starting_id, str(saved_state.starting_id))
    else:
        add_placeholder(starting_id, "0")

    # Header row (comes right after origin)
    header_frame = tk.Frame(rows_frame)
    header_frame.pack(anchor="w", fill="x")

    # Target rows appear below the header
    target_rows_frame = tk.Frame(rows_frame)
    target_rows_frame.pack(anchor="w", fill="x")
    target_rows: list[TargetRow] = []

    output_label = tk.Label(text_frame, text="", anchor="w", justify="left")
    output_label.pack(anchor="w")

    def resize_window_to_content() -> None:
        """Ensure the window is large enough for the current content, with margin.

        This updates the minimum size every time. The actual window size is only
        increased when the current size is too small, so a manually enlarged
        window is preserved.
        """
        root.update_idletasks()

        required_width = main_frame.winfo_reqwidth() + WINDOW_MARGIN_X
        required_height = main_frame.winfo_reqheight() + WINDOW_MARGIN_Y

        root.minsize(required_width, required_height)

        current_width = root.winfo_width()
        current_height = root.winfo_height()

        if current_width < required_width or current_height < required_height:
            new_width = max(current_width, required_width)
            new_height = max(current_height, required_height)
            root.geometry(f"{new_width}x{new_height}")

    def add_target_row() -> None:
        """Add one more target row below the targets header."""
        target_row = make_target_row(target_rows_frame, vcmd)
        target_rows.append(target_row)

        def remove_this_row(row=target_row):
            row.frame.destroy()
            target_rows.remove(row)
            resize_window_to_content()

        target_row.remove_btn.config(command=remove_this_row)

        resize_window_to_content()

    def on_make_schematic() -> None:
        """Preview the current values, choose an output path, and persist state."""
        output_path = filedialog.asksaveasfilename(
            parent=root,
            title="Save generated schematic as...",
            defaultextension=".litematic",
            filetypes=[("Litematic files", "*.litematic")],
        )
        if not output_path:
            return

        origin_xyz = format_coordinates(origin_entries, allow_placeholder=True)
        origin = Coordinates(x=origin_xyz[0], y=origin_xyz[1], z=origin_xyz[2])
        targets = collect_targets(target_rows)
        current_starting_id = get_int(starting_id, allow_placeholder=True)

        make_schematics(
            litematica_origin=origin,
            targets=targets,
            existing_targets_count=current_starting_id,
            output_path=output_path,
        )

        new_starting_id = current_starting_id + len(target_rows)

        save_state(
            SavedState(
                origin_x=origin.x,
                origin_y=origin.y,
                origin_z=origin.z,
                starting_id=new_starting_id,
            )
        )
        set_entry_text(starting_id, str(new_starting_id))

    make_targets_header_row(header_frame, add_target_row)

    tk.Button(buttons_frame, text="Make schematic", command=on_make_schematic).pack(side="left", padx=(0, BUTTON_GAP_X))
    tk.Button(buttons_frame, text="Close", command=root.destroy).pack(side="left")

    add_target_row()
    resize_window_to_content()
    root.mainloop()


if __name__ == "__main__":
    main()
