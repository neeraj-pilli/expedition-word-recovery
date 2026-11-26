import tkinter as tk
from tkinter import ttk, messagebox
import time


class TrieNode:
    """Node in a prefix tree (Trie) storing dictionary words."""
    __slots__ = ("children", "word")

    def __init__(self):
        self.children = {}
        self.word = None


class WordRecoveryEngine:
    """
    Combines a Trie for prefix pruning with 4-directional DFS + backtracking
    to find unique dictionary words and a valid coordinate path for each.
    """
    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

    def __init__(self, dictionary):
        self.root = TrieNode()
        self.word_count = 0
        self.build_trie(dictionary)

    def build_trie(self, dictionary):
        self.root = TrieNode()
        count = 0
        for raw_word in dictionary:
            word = raw_word.strip().lower()
            if not word or not word.isalpha():
                continue
            node = self.root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            if node.word is None:
                node.word = word
                count += 1
        self.word_count = count

    def search(self, grid, one_indexed=True):
        start_time = time.perf_counter()
        if not grid or not grid[0] or self.word_count == 0:
            return {}, {
                "nodes_visited": 0,
                "pruned_branches": 0,
                "elapsed_ms": 0.0,
            }

        rows = len(grid)
        cols = len(grid[0])
        visited = [[False] * cols for _ in range(rows)]
        results = {}
        nodes_visited = 0
        pruned_branches = 0

        def fmt_coord(r, c):
            return (r + 1, c + 1) if one_indexed else (r, c)

        def dfs(r, c, node, path):
            nonlocal nodes_visited, pruned_branches

            if r < 0 or r >= rows or c < 0 or c >= cols:
                return
            if visited[r][c]:
                return

            ch = grid[r][c]
            if ch not in node.children:
                pruned_branches += 1
                return

            next_node = node.children[ch]
            if not next_node.children and next_node.word is None:
                pruned_branches += 1
                return

            nodes_visited += 1
            visited[r][c] = True
            path.append(fmt_coord(r, c))

            if next_node.word is not None:
                results[next_node.word] = list(path)
                next_node.word = None

            if next_node.children:
                for dr, dc in self.DIRECTIONS:
                    dfs(r + dr, c + dc, next_node, path)

            path.pop()
            visited[r][c] = False

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, self.root, [])

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return results, {
            "nodes_visited": nodes_visited,
            "pruned_branches": pruned_branches,
            "elapsed_ms": elapsed_ms,
        }


SAMPLE_PRESETS = {
    "Illustrative Example (4x4)": {
        "grid": [
            ["o", "a", "a", "n"],
            ["e", "t", "a", "e"],
            ["i", "h", "k", "r"],
            ["i", "f", "l", "v"],
        ],
        "dictionary": ["oath", "pea", "eat", "rain"],
    },
    "Shared Prefixes & Repeats (5x5)": {
        "grid": [
            ["s", "t", "a", "r", "e"],
            ["a", "r", "t", "s", "t"],
            ["n", "d", "a", "r", "e"],
            ["d", "e", "a", "r", "s"],
            ["s", "t", "a", "r", "t"],
        ],
        "dictionary": [
            "star", "stars", "start", "starts", "stare", "stares",
            "art", "arts", "dart", "darts", "read", "reads",
            "sand", "sands", "stand", "stands", "trade", "trades",
            "rare", "rat", "rats", "tear", "tears", "ear", "ears"
        ],
    },
    "Empty Result / No Match (3x4)": {
        "grid": [
            ["x", "y", "z", "q"],
            ["m", "n", "p", "w"],
            ["b", "c", "d", "f"],
        ],
        "dictionary": ["expedition", "signal", "radio", "lost"],
    },
}


class WordRecoveryApp:
    """Desktop GUI for The Expedition's Lost Words recovery system with Blue Palette."""

    def __init__(self, root):
        self.root = root
        self.root.title("The Expedition's Lost Words — Word Recovery System")
        self.root.geometry("1120x740")
        self.root.minsize(920, 620)

        self.current_grid = []
        self.results = {}
        self.selected_word = None
        self.cell_buttons = []
        self.cell_step_labels = []

        self._setup_styles()
        self._build_ui()
        self._load_preset("Illustrative Example (4x4)")
        self._run_search()

    def _setup_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Elegant Professional Blue Color Palette
        self.bg_app = "#F0F4F8"           # Light Ice Blue background
        self.bg_card = "#FFFFFF"          # White container cards
        self.brand_blue = "#0F4C81"       # Classic Deep Royal Blue
        self.accent_blue = "#2563EB"      # Vibrant Primary Blue button
        self.accent_hover = "#1D4ED8"     # Darker Blue hover state
        self.path_start_bg = "#93C5FD"   # Soft Sky Blue for starting cell
        self.path_cell_bg = "#DBEAFE"    # Very light ice blue for path steps
        self.path_border = "#1E40AF"     # Deep Cobalt Blue for path outline
        self.text_dark = "#0F172A"       # Dark Slate Navy for text
        self.text_muted = "#475569"      # Cool Grey for secondary text
        self.grid_border = "#CBD5E1"     # Light grey-blue border for grid cells

        self.root.configure(bg=self.bg_app)
        style.configure("TFrame", background=self.bg_app)
        style.configure("Card.TFrame", background=self.bg_card, relief="groove", borderwidth=1)

        style.configure("Title.TLabel", background=self.bg_app, foreground=self.brand_blue,
                        font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", background=self.bg_app, foreground=self.text_muted,
                        font=("Segoe UI", 9))
        style.configure("Section.TLabel", background=self.bg_card, foreground=self.brand_blue,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Body.TLabel", background=self.bg_card, foreground=self.text_dark,
                        font=("Segoe UI", 9))

        style.configure("Primary.TButton", background=self.accent_blue, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"), padding=(12, 6))
        style.map("Primary.TButton",
                  background=[("active", self.accent_hover), ("pressed", self.accent_hover)])
        style.configure("TButton", font=("Segoe UI", 9), padding=(8, 5))

        # Styled Table with Ice Blue Headers and Royal Blue Selection Highlight
        style.configure("Treeview", background="#FFFFFF", foreground=self.text_dark,
                        fieldbackground="#FFFFFF", rowheight=24, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#EFF6FF", foreground=self.brand_blue,
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", "#3B82F6")],
                  foreground=[("selected", "#FFFFFF")])

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(16, 12, 16, 6))
        header.pack(fill="x")

        ttk.Label(header, text="The Expedition's Lost Words", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Trie Prefix Pruning + 4-Directional Backtracking DFS | Up to 10x10 Grid & 10,000 Words",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        main = ttk.Frame(self.root, padding=(16, 6, 16, 14))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1, minsize=340)
        main.columnconfigure(1, weight=2, minsize=520)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(2, weight=1)

        cfg_card = ttk.Frame(left, style="Card.TFrame", padding=12)
        cfg_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(cfg_card, text="1. Preset & Grid Dimensions", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        preset_row = ttk.Frame(cfg_card)
        preset_row.configure(style="Card.TFrame")
        preset_row.pack(fill="x", pady=(0, 8))
        ttk.Label(preset_row, text="Sample:", style="Body.TLabel").pack(side="left", padx=(0, 6))
        self.preset_var = tk.StringVar()
        preset_cb = ttk.Combobox(
            preset_row,
            textvariable=self.preset_var,
            values=list(SAMPLE_PRESETS.keys()) + ["Large Prefix Stress Test (10x10)"],
            state="readonly",
        )
        preset_cb.pack(side="left", fill="x", expand=True)
        preset_cb.bind("<<ComboboxSelected>>", lambda _e: self._load_preset(self.preset_var.get()))

        dim_row = ttk.Frame(cfg_card)
        dim_row.configure(style="Card.TFrame")
        dim_row.pack(fill="x")

        ttk.Label(dim_row, text="Rows (1-10):", style="Body.TLabel").pack(side="left")
        self.rows_var = tk.IntVar(value=4)
        ttk.Spinbox(dim_row, from_=1, to=10, width=4, textvariable=self.rows_var).pack(side="left", padx=(4, 12))

        ttk.Label(dim_row, text="Cols (1-10):", style="Body.TLabel").pack(side="left")
        self.cols_var = tk.IntVar(value=4)
        ttk.Spinbox(dim_row, from_=1, to=10, width=4, textvariable=self.cols_var).pack(side="left", padx=(4, 12))

        ttk.Button(dim_row, text="Resize", command=self._resize_grid).pack(side="right")

        grid_in_card = ttk.Frame(left, style="Card.TFrame", padding=12)
        grid_in_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(grid_in_card, text="2. Grid Letters (Lowercase, 1 per Row)", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(
            grid_in_card,
            text="Enter letters separated by spaces or contiguously (e.g., o a a n or oaan).",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        self.grid_text = tk.Text(grid_in_card, height=6, width=28, font=("Consolas", 10), wrap="none",
                                 bg="#F8FAFC", fg=self.text_dark, insertbackground=self.brand_blue)
        self.grid_text.pack(fill="x")

        dict_card = ttk.Frame(left, style="Card.TFrame", padding=12)
        dict_card.grid(row=2, column=0, sticky="nsew")
        dict_card.rowconfigure(1, weight=1)
        dict_card.columnconfigure(0, weight=1)

        ttk.Label(dict_card, text="3. Dictionary Words", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.dict_text = tk.Text(dict_card, height=8, width=28, font=("Consolas", 10), wrap="word",
                                 bg="#F8FAFC", fg=self.text_dark, insertbackground=self.brand_blue)
        self.dict_text.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        btn_row = ttk.Frame(dict_card)
        btn_row.configure(style="Card.TFrame")
        btn_row.grid(row=2, column=0, sticky="ew")

        self.one_idx_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_row, text="1-based (r,c)", variable=self.one_idx_var).pack(side="left")
        ttk.Button(btn_row, text="Clear Path", command=self._clear_highlight).pack(side="right", padx=(6, 0))
        ttk.Button(btn_row, text="Recover Words", style="Primary.TButton", command=self._run_search).pack(side="right")

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=3)
        right.rowconfigure(1, weight=2)
        right.columnconfigure(0, weight=1)

        board_card = ttk.Frame(right, style="Card.TFrame", padding=12)
        board_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        board_card.rowconfigure(1, weight=1)
        board_card.columnconfigure(0, weight=1)

        top_board = ttk.Frame(board_card)
        top_board.configure(style="Card.TFrame")
        top_board.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(top_board, text="Communication Panel & Path Highlighter", style="Section.TLabel").pack(side="left")
        self.path_summary_var = tk.StringVar(value="Select a recovered word below to highlight its path.")
        ttk.Label(board_card, textvariable=self.path_summary_var, style="Body.TLabel").grid(row=1, column=0, sticky="nwe")

        self.board_container = ttk.Frame(board_card)
        self.board_container.configure(style="Card.TFrame")
        self.board_container.grid(row=2, column=0, sticky="nsew", pady=8)

        self.stats_var = tk.StringVar(value="Ready.")
        ttk.Label(board_card, textvariable=self.stats_var, style="Subtitle.TLabel").grid(row=3, column=0, sticky="w")

        out_card = ttk.Frame(right, style="Card.TFrame", padding=12)
        out_card.grid(row=1, column=0, sticky="nsew")
        out_card.rowconfigure(1, weight=1)
        out_card.columnconfigure(0, weight=1)

        ttk.Label(out_card, text="Recovered Words & Coordinate Paths (Click Row to Highlight)", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        columns = ("word", "length", "path")
        self.tree = ttk.Treeview(out_card, columns=columns, show="headings", height=7)
        self.tree.heading("word", text="Word")
        self.tree.heading("length", text="Len")
        self.tree.heading("path", text="Coordinate Sequence")
        self.tree.column("word", width=130, anchor="w")
        self.tree.column("length", width=55, anchor="center")
        self.tree.column("path", width=440, anchor="w")

        scrollbar = ttk.Scrollbar(out_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_word_select)

    def _generate_stress_preset(self):
        grid = [
            ["p", "r", "e", "f", "i", "x", "a", "b", "c", "d"],
            ["e", "a", "r", "t", "h", "s", "t", "a", "r", "e"],
            ["s", "t", "a", "r", "t", "e", "d", "n", "o", "w"],
            ["p", "r", "e", "p", "a", "r", "e", "s", "e", "t"],
            ["a", "r", "t", "i", "s", "t", "s", "a", "n", "d"],
            ["r", "e", "a", "d", "i", "n", "g", "t", "r", "e"],
            ["e", "x", "p", "e", "d", "i", "t", "i", "o", "n"],
            ["s", "i", "g", "n", "a", "l", "s", "p", "a", "n"],
            ["t", "r", "a", "c", "e", "r", "s", "l", "o", "s"],
            ["w", "o", "r", "d", "s", "f", "o", "u", "n", "d"],
        ]
        prefixes = ["pre", "star", "art", "read", "sig", "trac", "word", "exp"]
        suffixes = ["", "s", "ed", "er", "ers", "ing", "al", "als", "tion", "ions", "ly"]
        dictionary = []
        for p in prefixes:
            for s in suffixes:
                dictionary.append(p + s)
        base_idx = 0
        while len(dictionary) < 10000:
            p = prefixes[base_idx % len(prefixes)]
            s = suffixes[(base_idx // len(prefixes)) % len(suffixes)]
            dictionary.append(f"{p}{s}")
            base_idx += 1
        return grid, dictionary

    def _load_preset(self, name):
        self.preset_var.set(name)
        if name == "Large Prefix Stress Test (10x10)":
            grid, dictionary = self._generate_stress_preset()
        else:
            preset = SAMPLE_PRESETS.get(name, SAMPLE_PRESETS["Illustrative Example (4x4)"])
            grid, dictionary = preset["grid"], preset["dictionary"]

        self.rows_var.set(len(grid))
        self.cols_var.set(len(grid[0]))

        self.grid_text.delete("1.0", "end")
        for row in grid:
            self.grid_text.insert("end", " ".join(row) + "\n")

        self.dict_text.delete("1.0", "end")
        self.dict_text.insert("1.0", "\n".join(dictionary))

    def _resize_grid(self):
        r_target = max(1, min(10, int(self.rows_var.get())))
        c_target = max(1, min(10, int(self.cols_var.get())))
        self.rows_var.set(r_target)
        self.cols_var.set(c_target)

        current_lines = self._parse_raw_grid_lines()
        new_lines = []
        for r in range(r_target):
            row_chars = current_lines[r] if r < len(current_lines) else []
            adjusted = (row_chars + ["a"] * c_target)[:c_target]
            new_lines.append(" ".join(adjusted))

        self.grid_text.delete("1.0", "end")
        self.grid_text.insert("1.0", "\n".join(new_lines))

    def _parse_raw_grid_lines(self):
        lines = []
        for raw in self.grid_text.get("1.0", "end").splitlines():
            cleaned = [ch.lower() for ch in raw.strip().replace(",", " ").split() if ch]
            if len(cleaned) == 1 and len(cleaned[0]) > 1:
                cleaned = list(cleaned[0])
            if cleaned:
                lines.append(cleaned)
        return lines

    def _parse_inputs(self):
        rows = max(1, min(10, int(self.rows_var.get())))
        cols = max(1, min(10, int(self.cols_var.get())))

        raw_lines = self._parse_raw_grid_lines()
        if len(raw_lines) != rows:
            raise ValueError(f"Expected {rows} grid rows, but found {len(raw_lines)}.")

        grid = []
        for idx, line in enumerate(raw_lines, start=1):
            if len(line) != cols:
                raise ValueError(f"Row {idx} must have {cols} letters, but found {len(line)}.")
            if any(not ch.isalpha() or len(ch) != 1 for ch in line):
                raise ValueError(f"Row {idx} contains non-letter tokens.")
            grid.append(line)

        raw_dict = self.dict_text.get("1.0", "end").replace(",", " ").split()
        dictionary = [w.strip().lower() for w in raw_dict if w.strip()]
        if len(dictionary) > 10000:
            raise ValueError(f"Dictionary limit is 10,000 words; got {len(dictionary)}.")
        if any(len(w) > 10 or not w.isalpha() for w in dictionary):
            raise ValueError("Dictionary words must be alphabetic and at most 10 characters long.")

        return grid, dictionary

    def _render_grid_board(self, grid):
        for widget in self.board_container.winfo_children():
            widget.destroy()

        self.cell_buttons = []
        self.cell_step_labels = []
        rows, cols = len(grid), len(grid[0])

        inner = ttk.Frame(self.board_container)
        inner.configure(style="Card.TFrame")
        inner.pack(expand=True)

        cell_size = 46 if max(rows, cols) <= 6 else 36
        font_size = 13 if max(rows, cols) <= 6 else 10

        for r in range(rows):
            btn_row = []
            step_row = []
            for c in range(cols):
                cell_frame = tk.Frame(
                    inner,
                    width=cell_size,
                    height=cell_size,
                    bg=self.bg_card,
                    highlightbackground=self.grid_border,
                    highlightthickness=1,
                )
                cell_frame.grid(row=r, column=c, padx=2, pady=2)
                cell_frame.grid_propagate(False)

                letter_lbl = tk.Label(
                    cell_frame,
                    text=grid[r][c],
                    bg=self.bg_card,
                    fg=self.text_dark,
                    font=("Consolas", font_size, "bold"),
                )
                letter_lbl.place(relx=0.5, rely=0.55, anchor="center")

                step_lbl = tk.Label(
                    cell_frame,
                    text="",
                    bg=self.bg_card,
                    fg=self.path_border,
                    font=("Segoe UI", 8, "bold"),
                )
                step_lbl.place(relx=0.80, rely=0.18, anchor="center")

                btn_row.append((cell_frame, letter_lbl, step_lbl))
                step_row.append(step_lbl)
            self.cell_buttons.append(btn_row)
            self.cell_step_labels.append(step_row)

    def _clear_highlight(self):
        self.selected_word = None
        for r in range(len(self.cell_buttons)):
            for c in range(len(self.cell_buttons[r])):
                frame, lbl, step_lbl = self.cell_buttons[r][c]
                frame.configure(bg=self.bg_card, highlightbackground=self.grid_border, highlightthickness=1)
                lbl.configure(bg=self.bg_card, fg=self.text_dark)
                step_lbl.configure(text="", bg=self.bg_card)
        self.path_summary_var.set("Select a recovered word below to highlight its path.")

    def _highlight_path(self, word, coords):
        self._clear_highlight()
        self.selected_word = word
        one_idx = self.one_idx_var.get()

        for step_idx, (pr, pc) in enumerate(coords, start=1):
            r = pr - 1 if one_idx else pr
            c = pc - 1 if one_idx else pc
            if 0 <= r < len(self.cell_buttons) and 0 <= c < len(self.cell_buttons[0]):
                frame, lbl, step_lbl = self.cell_buttons[r][c]
                bg_color = self.path_start_bg if step_idx == 1 else self.path_cell_bg
                text_color = "#1E3A8A" if step_idx == 1 else self.text_dark
                frame.configure(bg=bg_color, highlightbackground=self.path_border, highlightthickness=2)
                lbl.configure(bg=bg_color, fg=text_color)
                step_lbl.configure(text=str(step_idx), bg=bg_color, fg=self.path_border)

        chain = " -> ".join(f"({r},{c})" for r, c in coords)
        self.path_summary_var.set(f'Selected "{word}": {chain}')

    def _run_search(self):
        try:
            grid, dictionary = self._parse_inputs()
        except ValueError as exc:
            messagebox.showerror("Invalid Input", str(exc))
            return

        self.current_grid = grid
        self._render_grid_board(grid)

        engine = WordRecoveryEngine(dictionary)
        one_idx = self.one_idx_var.get()
        self.results, stats = engine.search(grid, one_indexed=one_idx)

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.results:
            self.tree.insert("", "end", values=("(No words found)", "-", "Empty result for current grid & dictionary"))
            self.path_summary_var.set("No matching dictionary words found in the grid.")
        else:
            for word in sorted(self.results.keys()):
                coords = self.results[word]
                chain = " -> ".join(f"({r},{c})" for r, c in coords)
                self.tree.insert("", "end", iid=word, values=(word, len(word), chain))

            first_word = sorted(self.results.keys())[0]
            self.tree.selection_set(first_word)
            self._highlight_path(first_word, self.results[first_word])

        self.stats_var.set(
            f"Unique Trie Words: {engine.word_count} | Found: {len(self.results)} | "
            f"DFS Nodes: {stats['nodes_visited']} | Pruned: {stats['pruned_branches']} | "
            f"Time: {stats['elapsed_ms']:.2f} ms"
        )

    def _on_word_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        word = sel[0]
        if word in self.results:
            self._highlight_path(word, self.results[word])


def main():
    root = tk.Tk()
    WordRecoveryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
