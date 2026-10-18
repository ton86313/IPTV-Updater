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

    # 1. ค้นหาด้วย Regex ทั่วทั้งหน้าเว็บสำหรับลิงก์ที่ลงท้ายหรือมี .mp4
    pattern = r'https?://[^\s"\'<>]+?\.mp4[^\s"\'<>]*'
    matches = re.findall(pattern, response.text)
    if matches:
      for url in matches:
        clean_url = url.strip('"\'')
        print(f"✅ พบลิงก์จาก Regex: {clean_url}")
        return clean_url

    # 2. ค้นหาในทุกๆ แท็กและแอตทริบิวต์ (เช่น src, data-src) ของ HTML
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
    print("⚠️ ข้ามการอัปเดตไฟล์ M3U เนื่องจากไม่พบลิงก์")
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
