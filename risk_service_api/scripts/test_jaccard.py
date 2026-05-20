def trigram_jaccard(a, b):
    def trigrams(text):
        text = text.strip()
        return {text[i:i+3] for i in range(len(text) - 2)} if len(text) >= 3 else {text}
    sa = trigrams(a)
    sb = trigrams(b)
    return len(sa & sb) / len(sa | sb)

chunks = [
    "ผู้ป่วยต้องไม่บ้วนปากแรงจนก้อนเลือดหลุดจากเบ้าแผล",
    "ต้องไม่บ้วนปากแรงหลังถอนฟันเพราะอาจทำให้ก้อนเลือดหลุด",
    "หลังการถอนฟันหรือผ่าฟันคุด ห้ามบ้วนกลั้วปากแรงเกินไป เพราะจะทำให้ก้อนเลือดที่ปิดปากแผลหลุดออกมา",
    "หลังการถอนฟันหรือผ่าฟันคุด ห้ามบ้วนกลั้วปากแรงเกินไป",
    "กัดผ้าก๊อซไว้นิ่งๆ ประมาณ 1 ชั่วโมง",
    "ออกกำลังกายได้ แต่ต้องไม่หนักเกินไป",
]
for i in range(len(chunks)):
    for j in range(i+1, len(chunks)):
        sim = trigram_jaccard(chunks[i], chunks[j])
        mark = " ← DUPLICATE" if sim > 0.5 else ""
        print(f"Chunk {i+1} vs {j+1}: Jaccard = {sim:.3f}{mark}")
