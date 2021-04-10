import argparse
import json
import os
import re
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Removes HTML tags from Hansard speeches in JSON with some filters")
parser.add_argument("path", type=str, help="path to Hansard JSON file")
parser.add_argument("--non_session", action="store_true",
                    help="Invoke parser for partial Hansard sessions, (e.g. bills, motions)")
parser.add_argument("-g", "--granular", action="store_true",
                    help="enable granular options for removal of text (see below)")
parser.add_argument("-v", "--vernacular", action="store_true",
                    help="remove vernacular references from text (e.g. 'In Mandarin')")
parser.add_argument("-a", "--applause", action="store_true",
                    help="remove applauses from text (e.g. '[Applause]')")
parser.add_argument("-t", "--timestamp", action="store_true",
                    help="remove timestamps from text (e.g. '1.18pm')")
parser.add_argument("-p", "--procedural", action="store_true",
                    help="remove procedural text demarcated by (proc test)")
parser.add_argument("-pg", "--pages", action="store_true",
                    help="remove page numbers")

if __name__ == "__main__":
    args = parser.parse_args()

    with open(args.path, "rb") as f:
        raw_data = json.load(f)

    cwd = os.getcwd()
    if not os.path.exists(os.path.join(cwd, "output")):
        os.mkdir("output")
    output_path = os.path.join(cwd, "output", os.path.basename(args.path)[:-5] + "_formatted.json")

    if args.non_session:
        speeches = [raw_data["resultHTML"]]
    else:
        speeches = raw_data["takesSectionVOList"]

    sessions = []
    speaker_list = {}
    for raw_speech in speeches:
        out_json = {}
        html_content = raw_speech["content"]
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator='\n')

        if args.vernacular or not args.granular:
            text = re.sub(r"\(\s+In Mandarin\s+\)\s+:\s+\[\s+Please refer to\s+Vernacular Speech\n+\.]", "", text)
            text = re.sub(r"\(\s+In Malay\s+\)\s+:\s+\[\s+Please refer to\s+Vernacular Speech\n+\.]", "", text)
            text = re.sub(r"\(\s*In English\s*\):?", "", text)
            text = re.sub(r"\(\s*In Malay\s*\):?", "", text)
            text = re.sub(r"\(\s*In Mandarin\s*\):?", "", text)

        if args.applause or not args.granular:
            text = re.sub(r"\[\s+Applause.?\s+]", "", text)

        if args.timestamp or not args.granular:  # only matches timestamps that are in its own line
            text = re.sub(r"[\r\n]+\d{1,2}\.\d{2}[ ]?[ap]m[\r\n]", "\n", text)

        if args.procedural or not args.granular:
            text = re.sub(r"\[\(proc text\).+?\(proc text\)]", "", text)

        if args.pages or not args.granular:
            text = re.sub(r"\sPage: \d{1,4}\s", "", text)

        pre_text = text.split('\n')

        # Generate list of speakers
        curr_speaker_list = list(soup.find_all("strong"))
        curr_speaker_list = list(set(map(lambda x: re.sub(r"<.+?>", "", str(x)).strip(), curr_speaker_list)))
        curr_speaker_list = list(filter(lambda x: x.strip() != "The Chairman", curr_speaker_list))

        # Generate dictionary of speakers to names for formatting later
        clean_speakers = {}
        for i in range(len(curr_speaker_list)):
            speaker = curr_speaker_list[i]
            if speaker.find("(") != -1:
                parts = speaker.split("(")
                if parts[0].find("Minister") != -1 or parts[0].find("Leader") != -1:
                    if parts[1].lower().find("schools") != -1 or parts[1].lower().find("education") != -1:
                        name = parts[2].split(")")[0]
                    else:
                        name = parts[1].split(")")[0]
                else:
                    name = parts[0].strip()
            else:
                name = speaker.strip()
            if len(name) > 0:
                clean_speakers[speaker] = name

        # Update list of speakers
        speaker_list.update(clean_speakers)
        speech_json = []

        # Extract speeches, labelling with speaker name when encountered
        current_speaker = ""
        current_speech = []
        for line in pre_text:
            sline = line.strip().replace('\u009d', "")
            if sline in speaker_list:
                if current_speaker and current_speech:
                    d = {"speaker": speaker_list[current_speaker], "content": current_speech.copy()}
                    speech_json.append(d.copy())
                current_speaker = sline
                current_speech.clear()
                continue
            if sline:
                current_speech.append(sline)

        if current_speaker and current_speech:
            d = {"speaker": speaker_list[current_speaker], "content": current_speech.copy()}
            speech_json.append(d.copy())

        # Save to Json
        out_json["title"] = raw_speech["title"]
        out_json["speeches"] = speech_json.copy()
        out_json["speakers"] = list(set(clean_speakers.values()))

        sessions.append(out_json.copy())

    with open(output_path, "w", encoding="UTF-8") as f:
        json.dump({"filename": args.path, "sessions": sessions, "all_speakers": list(set(speaker_list.values()))},
                  f, indent=2, ensure_ascii=False)
