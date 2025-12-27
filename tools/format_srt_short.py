import sys
from pathlib import Path
import textwrap

def format_srt(input_path: str):
    input_path = Path(input_path)
    output_path = input_path.with_name(
        input_path.stem + "_clean.srt"
    )

    with open(input_path, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")

    cleaned = []

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue

        idx = lines[0]
        time = lines[1]
        text = " ".join(lines[2:])

        wrapped = textwrap.fill(text, width=35)

        cleaned.append(
            f"{idx}\n{time}\n{wrapped}"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(cleaned))

    print("✅ SRT nettoyé :", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python format_srt_short.py <file.srt>")
        sys.exit(1)

    format_srt(sys.argv[1])
