import os
import re
from bs4 import BeautifulSoup
import cloudscraper

WEB_PAGE_URL = "https://bunkr.ws/f/WrWkgiCtY4dTc"
M3U_FILENAME = "IPTV-Marco.m3u"


def fetch_latest_video_url():
  try:
    print(f"กำลังเชื่อมต่อไปยัง: {WEB_PAGE_URL}")
    scraper = cloudscraper.create_scraper()
    response = scraper.get(WEB_PAGE_URL, timeout=10)
    print(f"สถานะการเชื่อมต่อ: {response.status_code}")

    if response.status_code != 200:
      print(f"❌ ไม่สามารถเข้าถึงหน้าเว็บได้ (Status: {response.status_code})")
      return None

    # 1. ค้นหาด้วย Regex ทั่วทั้งหน้าเว็บสำหรับลิงก์ .mp4 ที่มี token
    pattern = r'https?://[^\s"\'<>]+?\.mp4[^\s"\'<>]*'
    matches = re.findall(pattern, response.text)
    if matches:
      for url in matches:
        if "cdn" in url or "storage" in url or "?" in url:
          clean_url = url.strip('"\'')
          print(f"✅ พบลิงก์วิดีโอ: {clean_url}")
          return clean_url
      clean_url = matches[0].strip('"\'')
      print(f"✅ พบลิงก์วิดีโอ (สำรอง): {clean_url}")
      return clean_url

    # 2. ค้นหาในแท็ก HTML ทั่วไป
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup.find_all(True):
      for attr in tag.attrs:
        val = tag.get(attr)
        if isinstance(val, str) and ".mp4" in val:
          clean_url = val.strip('"\'')
          print(f"✅ พบลิงก์ใน Attribute [{attr}]: {clean_url}")
          return clean_url

    print("❌ ไม่พบลิงก์วิดีโอในหน้าเว็บ")
    return None
  except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    return None


def update_m3u():
  new_url = fetch_latest_video_url()
  if not new_url:
    print("⚠️ ข้ามการอัปเดต เนื่องจากไม่พบลิงก์ใหม่")
    return

  # ตรวจสอบว่ามีไฟล์เดิมอยู่หรือไม่ ถ้ามีให้อ่านเนื้อหาเดิมเก็บไว้
  existing_content = ""
  if os.path.exists(M3U_FILENAME):
    with open(M3U_FILENAME, "r", encoding="utf-8") as f:
      existing_content = f.read()

  # ถ้าลิงก์ใหม่นี้มีอยู่แล้วในไฟล์เดิม ไม่ต้องเพิ่มซ้ำ
  if new_url in existing_content:
    print("ℹ️ ลิงก์นี้มีอยู่ในรายการอยู่แล้ว ไม่มีการเปลี่ยนแปลง")
    return

  # สร้างรายการใหม่ที่จะเพิ่มต่อท้าย
  new_entry = f'#EXTINF:-1 group-title="คลิป" tvg-logo="https://static.scdn.st/027e12ae-683b-4e42-950f-2b3f12448931/thumbs/cc0433e0-c396-4305-8c92-1f792ef9803f.png",cy-102\n{new_url}\n'

  if "#EXTM3U" not in existing_content:
    # หากยังไม่มีหัวไฟล์ M3U ให้สร้างใหม่
    final_content = f"#EXTM3U\n{new_entry}"
  else:
    # หากมีไฟล์เดิมอยู่แล้ว ให้ต่อท้ายรายการเดิมโดยไม่ลบของเก่า
    final_content = existing_content.strip() + "\n" + new_entry

  # บันทึกไฟล์กลับลงไป
  with open(M3U_FILENAME, "w", encoding="utf-8") as f:
    f.write(final_content)
  print(f"✅ เพิ่มลิงก์ใหม่ลงในไฟล์ {M3U_FILENAME} สำเร็จ (รายการเก่าอยู่ครบ)!")


if __name__ == "__main__":
  update_m3u()
