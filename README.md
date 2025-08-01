﻿# CKY Visualizer GUI

A lightweight, multilingual desktop application to run and visualize the Cocke–Younger–Kasami (CKY) parsing algorithm on your own CNF grammars and sentences, with dynamic tables, back-pointer arrows and derivation trees in Portuguese, English and French.

![App Screenshot](cky.png)

---

## 🔍 What’s This Project?

This friendly Tkinter GUI lets you:

- **Paste or type** your CNF grammar (one rule per line) and a test sentence.
- **Compute the CKY table** (bottom-up chart) with all non-terminal sets.
- **Draw back-pointer arrows** inside the table to show how each constituent was built.
- **Render the parse tree** side by side, automatically skipping duplicate terminals.
- **Switch languages** (🇵🇹 PT, 🇬🇧 EN, 🇫🇷 FR) and see all labels and menus update live.
- **Resize and scroll** the table and tree panes for longer inputs.

---

## 📚 Why CKY?

The CKY algorithm is a classic dynamic-programming parser for Context-Free Grammars in Chomsky Normal Form:

1. **Bottom-up parsing** fills a triangular chart of possible constituents.
2. **Back-pointers** record which split and pair of non-terminals produced each parent.
3. **Tree reconstruction** follows pointers from the root “S” cell to terminals.
4. Widely taught in compilers, NLP and formal language courses for its clarity and O(n³) efficiency.

---

## 📝 Example Workflow

1. **Enter a CNF grammar**:

   ```txt
   S -> NP VP
   NP -> Det N
   VP -> V NP
   Det -> As | muita
   N -> verdades | gente
   V -> incomodam
   ```

2. **Type the sentence**:

   ```
   As verdades incomodam muita gente
   ```

3. **Click Calculate** →

   - Left pane shows the CKY triangular table, arrows pointing to the derivation splits.
   - Right pane draws the final syntax tree with terminals in blue.

---

## 🚀 Installation & Usage

```bash
git clone https://github.com/bazucas/CKY-CNF-Visualizer.git
cd CKY-Visualizer
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

python cky-cnf-visualizer.py
```

---

## 📄 License

MIT © 2025

Feel free to use, fork, and contribute!
