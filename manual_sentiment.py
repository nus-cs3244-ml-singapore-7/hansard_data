import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="UTF-8") as f:
    ans = []
    for line in f:
        sentiment = None
        while sentiment is None:
            print("---")
            print(line)
            sentiment = input("POS/+/1 or NEG/-/0 sentiment? X to skip. ").strip()
            if sentiment in ["1", "POS", "+"]:
                sentiment = 1
            elif sentiment in ["0", "NEG", "-"]:
                sentiment = 0
            elif sentiment == "X":
                continue
            else:
                sentiment = None
        d = {"text": line, "sentiment": sentiment}
        ans.append(d)

output = path.split("_")[0] + "_sentiment.json"
with open(output, "w", encoding="UTF-8") as f:
    json.dump(ans, f)

print("Done!")
