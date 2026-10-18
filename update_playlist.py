import os
import re
import requests

WEB_PAGE_URL = "https://bunkr.ws/f/WrWkgiCtY4dTc"
M3U_FILENAME = "IPTV-Marco.m3u"


def fetch_latest_video_url():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    print("กำลังเชื่อมต่อดึงข้อมูลจากหน้าเว็บ...")
    response = requests.get(WEB_PAGE_URL, headers=headers, timeout=15)
    print(f"เชื่อมต่อสำเร็จ (Status Code: {response.status_code})")

    # ค้นหาลิงก์วิดีโอรูปแบบหลัก
    match = re.search(
        r'https://[^\s<"]+?\.cdn\.cr/storage/media/[^\s<"]+?\.mp4\?token=[^\s<"]+?&ex=\d+',
        response.text,
    )
    if match:
      return match.group(0)

    # ค้นหาแบบสำรองกรณีเปลี่ยนโครงสร้าง
    match_alt = re.search(r'https://[^\s<"]+?\.mp4\?[^\s<"]+', response.text)
    if match_alt:
      return match_alt.group(0)

    print("❌ ไม่พบลิงก์วิดีโอในหน้าเว็บ")
    return None
  except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    return None


def update_m3u():
  new_url = fetch_latest_video_url()
  if not new_url:
    print("❌ ข้ามการสร้างไฟล์เนื่องจากไม่พบลิงก์")
    return

  m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="คลิป" tvg-logo="https://static.scdn.st/027e12ae-683b-4e42-950f-2b3f12448931/thumbs/cc0433e0-c396-4305-8c92-1f792ef9803f.png",cy-102
{new_url}
"""
  with open(M3U_FILENAME, "w", encoding="utf-8") as f:
    f.write(m3u_content)
  print(f"✅ สร้าง/อัปเดตไฟล์ {M3U_FILENAME} สำเร็จ!")


if __name__ == "__main__":
  update_m3u()
