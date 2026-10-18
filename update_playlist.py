import re
import cloudscraper

WEB_PAGE_URL = "https://bunkr.ws/f/WrWkgiCtY4dTc"
M3U_FILENAME = "IPTV-Marco.m3u"


def fetch_latest_video_url():
  try:
    print(f"กำลังเชื่อมต่อผ่าน Cloudscraper ไปยัง: {WEB_PAGE_URL}")
    scraper = cloudscraper.create_scraper()
    response = scraper.get(WEB_PAGE_URL, timeout=15)
    print(f"สถานะการเชื่อมต่อ: {response.status_code}")

    # ค้นหาลิงก์ .mp4 ทั่วทั้งหน้า HTML
    matches = re.findall(r'https?://[^\s"\'<>]+?\.mp4[^\s"\'<>]*', response.text)
    if matches:
      for url in matches:
        if "cdn" in url or "storage" in url:
          clean_url = url.strip('"\'')
          print(f"✅ พบลิงก์วิดีโอจริง: {clean_url}")
          return clean_url
      clean_url = matches[0].strip('"\'')
      print(f"✅ พบลิงก์วิดีโอ: {clean_url}")
      return clean_url

    print("❌ ไม่พบลิงก์วิดีโอ .mp4 ในหน้าเว็บ")
    return None
  except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    return None


def update_m3u():
  new_url = fetch_latest_video_url()
  if not new_url:
    print("⚠️ ไม่มีการอัปเดตไฟล์ M3U เนื่องจากหาลิงก์วิดีโอไม่พบ")
    return

  m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="คลิป" tvg-logo="https://static.scdn.st/027e12ae-683b-4e42-950f-2b3f12448931/thumbs/cc0433e0-c396-4305-8c92-1f792ef9803f.png",cy-102
{new_url}
"""
  with open(M3U_FILENAME, "w", encoding="utf-8") as f:
    f.write(m3u_content)
  print(f"✅ อัปเดตไฟล์ {M3U_FILENAME} สำเร็จเรียบร้อย!")


if __name__ == "__main__":
  update_m3u()
