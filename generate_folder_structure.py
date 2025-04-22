import os

# Dışlanacak klasör ve dosya uzantıları
excluded_dirs = {
    "luna_env", ".vscode", ".idea", "__pycache__",
    "realImages", "thumbnails", "new_inputs",
    "exported_clusters",".git"
}

excluded_exts = {
    ".pyc", ".pkl", ".pt", ".index", ".npy", ".npz",
    ".log", ".tmp", ".bak", ".DS_Store", "Thumbs.db","zip"
}

excluded_files = {
    "image_metadata_map.json",
    "metadata_cache.json",
    "train_config.json"
}

output_file = "folder_structure.txt"

def write_structure(root_dir):
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(root_dir):
            # .gitignore mantığıyla filtrele
            rel_root = os.path.relpath(root, root_dir)
            if any(x in rel_root.split(os.sep) for x in excluded_dirs):
                continue

            indent_level = rel_root.count(os.sep)
            indent = "    " * indent_level
            f.write(f"{indent}{os.path.basename(root)}/\n")

            for file in files:
                ext = os.path.splitext(file)[1]
                if file in excluded_files or ext in excluded_exts:
                    continue

                f.write(f"{indent}    {file}\n")

    print(f"📂 Yapı oluşturuldu: {output_file}")

if __name__ == "__main__":
    write_structure(".")
