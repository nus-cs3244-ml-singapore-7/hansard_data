import json
import sys


input = sys.argv[1]
with open(input, "r", encoding="UTF-8") as f:
    raw_data = json.load(f)

output = input.split("_formatted")[0] + "_text.txt"
with open(output, "w", encoding="UTF-8") as f:
    for session in raw_data["sessions"]:
        f.write("~~~\n")
        f.write(session["title"] + "\n")
        for speech in session["speeches"]:
            f.write("|||\n")
            f.write(speech["speaker"] + "\n")
            f.write('\n'.join(speech["content"]))
            f.write('\n')
