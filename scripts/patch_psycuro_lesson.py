import os
import re

INDEX_PATH = os.path.join("docs", "index.html")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run this script from your repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if "1ps0SOVIX5M" in html:
        print("Video 1ps0SOVIX5M is already present in docs/index.html!")
        return

    video_entry_js = """        {
          id: 'kv_yt_psycuro_1ps0SOVIX5M',
          title: 'Teach Yourself Anything So Well It Feels Unfair',
          domain: 'Doctoral Studies',
          resourceFormat: 'YouTube Video Reference',
          author: 'Psycuro (@Psycuro) • Deslauriers, Gruber, Ericsson, Gollwitzer',
          sectionRef: '07:33 Five Moves • 07:45 Info Gap • 08:37 Generation Effect • 09:34 Feedback • 10:41 Teach • 11:21 Implementation Intentions',
          researchGap: 'Overcoming passive "feeling of learning" (Deslauriers et al., 2019) via generation effect, deliberate feedback, and implementation intentions.',
          duration: '12-Min Visual & Recall Sprint',
          type: 'Doctoral Studies • YouTube Video',
          videoId: '1ps0SOVIX5M',
          videoUrl: 'https://youtu.be/1ps0SOVIX5M?si=pmwMDumth8t9p3Vc',
          channelName: 'Psycuro',
          timestampAnchor: '07:33 Five Moves | 07:45 Move 1: Question | 08:37 Move 2: Generation | 09:34 Move 3: Checked | 10:41 Move 4: Teach | 11:21 Move 5: Time & Place',
          takeaway: 'Passive consumption creates an illusion of competence; true mastery requires 5 moves: (1) Information Gap question, (2) Generation Effect from memory, (3) External calibration/checking, (4) Teaching publicly, and (5) Implementation Intentions.',
          content: 'Key Timestamps: 07:33 Five moves to become dangerously self-educated. 07:45 Move 1: Start with a question (Information Gap — Loewenstein 1994; Gruber et al., 2014 Neuron). 08:37 Move 2: Rebuild it from memory (Generation Effect — Slamecka & Graf, 1978; Deslauriers et al., 2019 PNAS). 09:34 Move 3: Find a way to be checked (Deliberate Practice — Ericsson et al., 1993; Kruger & Dunning, 1999). 10:41 Move 4: Teach it in public (Learning by Teaching — Fiorella & Mayer, 2013). 11:21 Move 5: Give it a time and a place (Implementation Intentions — Gollwitzer & Sheeran, 2006).',
          microSteps: [
            '1. Moves 1 & 2 (07:45–08:37): Open an Information Gap with a specific question before reading, then close the source and rebuild the model from blank-page memory (Generation Effect).',
            '2. Moves 3 & 4 (09:34–10:41): Test against reality to defeat the illusion of competence (Deslauriers et al., 2019) and explain the concept aloud or in writing.',
            '3. Move 5 (11:21): Anchor study execution with Implementation Intentions ("After Fajr/Dhuhr at my desk, I will execute 1 recall block").'
          ],
          quiz: [
            { q: '1. According to Deslauriers et al. (2019) and Psycuro, why is passive video/reading consumption deceptive?', a: 'Passive fluency produces a high "feeling of learning" while yielding significantly lower actual retention and transfer than active generation.' },
            { q: '2. What are the 5 moves to become dangerously self-educated (07:33–11:21)?', a: '(1) Start with a question (Information Gap), (2) Rebuild from memory (Generation Effect), (3) Find a way to be checked, (4) Teach it in public, and (5) Give it a time and a place (Implementation Intentions).' },
            { q: '3. Applied Synthesis: How does Hive Alignment automate Move 2, Move 3, and Move 5 for your January 2027 Doctoral Prep?', a: 'Move 2 & 3 are enforced via blank-input 3Q Active-Recall Quizzes, and Move 5 is locked to live Fajr/Dhuhr Salat windows.' }
          ],
          masteryLevel: 0,
          nextReviewDate: new Date().toISOString().split('T')[0],
          quizScore: null,
          date: '2026-11-18'
        },"""

    target_marker = "      knowledgeVault: [\n"
    assert target_marker in html, "Could not locate knowledgeVault array in docs/index.html"
    html = html.replace(target_marker, target_marker + video_entry_js + "\n", 1)

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"
    print(f"Successfully added 'Teach Yourself Anything So Well It Feels Unfair' (1ps0SOVIX5M) to {INDEX_PATH}!")


if __name__ == "__main__":
    main()
