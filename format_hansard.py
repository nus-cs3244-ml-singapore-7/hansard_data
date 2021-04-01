import argparse
import json
import os
import re
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Removes HTML tags from Hansard speeches in JSON with some filters")
parser.add_argument("path", type=str, help="path to Hansard JSON file")
parser.add_argument("-s", "--session", action="store_true",
                    help="Invoke parser for full hansard sessions, else parse other formats (e.g. bills, motions)")
parser.add_argument("-f", "--full", action="store_true",
                    help="remove ALL peripheral text (see below)")
parser.add_argument("-v", "--vernacular", action="store_true",
                    help="remove vernacular references from text (e.g. 'In Mandarin')")
parser.add_argument("-a", "--applause", action="store_true",
                    help="remove applauses from text (e.g. '[Applause]')")
parser.add_argument("-t", "--timestamp", action="store_true",
                    help="remove timestamps from text (e.g. '1.18pm')")
parser.add_argument("-p", "--procedural", action="store_true",
                    help="remove procedural text demarcated by (proc test)")

if __name__ == "__main__":
    args = parser.parse_args()

    with open(args.path, "rb") as f:
        raw_data = json.load(f)

    cwd = os.getcwd()
    if not os.path.exists(os.path.join(cwd, "output")):
        os.mkdir("output")
    output_path = os.path.join(cwd, "output", os.path.basename(args.path)[:-5] + "_formatted.json")

    if args.session:
        speeches = raw_data["takesSectionVOList"]
    else:
        speeches = [raw_data["resultHTML"]]

    sessions = []
    for raw_speech in speeches:
        out_json = {}
        html_content = raw_speech["content"]
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator='\n')

        if args.vernacular or args.full:
            text = re.sub(r"\(\s+In Mandarin\s+\)\s+:\s+\[\s+Please refer to\s+Vernacular Speech\n+\.]", "", text)
            text = re.sub(r"\(\s+In Malay\s+\)\s+:\s+\[\s+Please refer to\s+Vernacular Speech\n+\.]", "", text)
            text = re.sub(r"\(\s*In English\s*\):?", "", text)
            text = re.sub(r"\(\s*In Malay\s*\):?", "", text)
            text = re.sub(r"\(\s*In Mandarin\s*\):?", "", text)

        if args.applause or args.full:
            text = re.sub(r"\[\s+Applause.?\s+]", "", text)

        if args.timestamp or args.full:  # only matches timestamps that are in its own line
            text = re.sub(r"[\r\n]+\d{1,2}\.\d{2}[ ]?[ap]m[\r\n]", "\n", text)

        if args.procedural or args.full:
            text = re.sub(r"\[\(proc text\).+?\(proc text\)]", "", text)

        pre_text = text.split('\n')
        speaker_list = list(soup.find_all("strong"))
        speaker_list = list(set(map(lambda x: re.sub(r"<.+?>", "", str(x)).strip(), speaker_list)))
        speech_json = []

        current_speaker = ""
        current_speech = []
        for line in pre_text:
            sline = line.strip().replace('\u009d', "")
            if sline in speaker_list:
                if current_speaker and current_speech:
                    d = {"speaker": current_speaker, "content": current_speech.copy()}
                    speech_json.append(d.copy())
                current_speaker = sline
                current_speech.clear()
                continue
            if sline:
                current_speech.append(sline)

        if current_speech:
            d = {"speaker": current_speaker, "content": current_speech.copy()}
            speech_json.append(d.copy())

        out_json["title"] = raw_speech["title"]
        out_json["speeches"] = speech_json.copy()
        out_json["speakers"] = speaker_list.copy()

        sessions.append(out_json.copy())

    with open(output_path, "w", encoding="UTF-8") as f:
        json.dump({"filename": args.path, "sessions": sessions}, f, indent=2, ensure_ascii=False)
