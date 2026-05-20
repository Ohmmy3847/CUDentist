# LINE OA Setup

## Rich Menu (สำหรับการลงทะเบียน)

เป้าหมาย: ทำให้คนไข้ “กดปุ่ม” แทนการเดาเองว่าจะพิมพ์อะไร

### ตั้งค่า Rich Menu ใน LINE OA Manager

1. เข้า LINE Official Account Manager → Rich menu
2. สร้างเมนูอย่างน้อย 2 ปุ่ม:
   - ปุ่ม `ลงทะเบียน` → **Action type: Send message** → ข้อความ: `register`
   - ปุ่ม `ช่วยเหลือ` → **Action type: Send message** → ข้อความ: `help`
3. Publish และตั้งเป็น Default rich menu

> Backend รองรับทั้งพิมพ์/กด `register`/`help` แล้ว

### รูปแบบการลงทะเบียนที่แนะนำ (case_code only)

- คนไข้กด `ลงทะเบียน` → ระบบตอบวิธีใช้งาน + ตัวอย่างรหัส
- คนไข้พิมพ์รหัส 6 ตัว เช่น `ABC123` → ระบบผูกบัญชีให้

## Dev Session (ทำทุกครั้ง)

```bash
# 1. รัน backend
cd backend && uvicorn main:app --port 8001 --reload

# 2. terminal ใหม่ — expose tunnel
cloudflared tunnel --url http://localhost:8001

# 3. copy URL → ไปอัพเดทใน LINE OA Manager
# Settings → Messaging API → Webhook URL
# https://<new-url>.trycloudflare.com/backend/line/webhook
```

## Dev Session (frontend)

```bash
cd frontend && npm run dev
```

## .env ที่ต้องใส่

```env
LINE_CHANNEL_SECRET=6e8043e7a0e64f00f71989211e8a118c
LINE_CHANNEL_ACCESS_TOKEN=<จาก LINE Developers Console → Messaging API → Issue>
LINE_SEND_WINDOW_HOURS=2
```

## Migration (ครั้งแรกครั้งเดียว)

```bash
cd backend && alembic upgrade head
```

## TODO

- [ ] ใส่ LINE_CHANNEL_ACCESS_TOKEN ใน .env
- [ ] รัน alembic upgrade head
- [ ] ทดสอบ webhook (กด Verify ใน LINE OA Manager)
- [ ] Implement แจ้งผลพยาบาล (email + web)
- [ ] Implement แจ้งผลคนไข้ (push LINE message หลัง submit)
