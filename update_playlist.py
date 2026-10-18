import re
from bs4 import BeautifulSoup
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
    print(f"กำลังดึงข้อมูลจาก: {WEB_PAGE_URL}")
    response = requests.get(WEB_PAGE_URL, headers=headers, timeout=15)
    print(f"สถานะการเชื่อมต่อ: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # ค้นหาจากแท็ก <source> ที่มี .mp4 อยู่ด้านใน (ตรงกับโครงสร้างใน DevTools)
    source_tag = soup.find(
        "source", src=lambda x: x and ".mp4" in x
    )
    if source_tag and source_tag.get("src"):
      url = source_tag["src"]
      print(f"✅ พบลิงก์จากแท็ก source: {url}")
      return url

    # ค้นหาเผื่อกรณีที่เป็นแท็ก video มี src โดยตรง
    video_tag = soup.find(
        "video", src=lambda x: x and ".mp4" in x
    )
    if video_tag and video_tag.get("src"):
      url = video_tag["src"]
      print(f"✅ พบลิงก์จากแท็ก video: {url}")
      return url

    # ค้นหาสำรองด้วย Regular Expression ทั่วทั้งหน้า HTML
    matches = re.findall(r'https://[^\s"<>]+?\.mp4\?[^\s"<>]+', response.text)
    if matches:
      url = matches[0].strip('"\'')
      print(f"✅ พบลิงก์จาก Regex: {url}")
      return url

    print("❌ ไม่พบลิงก์วิดีโอในหน้าเว็บ")
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
