import os
import datetime
import asyncio
import feedparser
import edge_tts
import xml.etree.ElementTree as ET

# RSS Sources for Malayalam News
SOURCES = [
    "https://www.manoramaonline.com/news/latest-news.rss",
    "https://www.mathrubhumi.com/rss/latest-news.xml"
]

def get_latest_headlines():
    headlines = []
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                headlines.append(entry.title.strip())
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return list(dict.fromkeys(headlines))[:8]

def build_script(headlines):
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    intro = f"നമസ്കാരം. ഇന്നത്തെ പ്രധാന വാർത്തകൾ. {today}. "
    body = " ... ".join(headlines)
    outro = " ... കൂടുതൽ വാർത്തകൾ അടുത്ത പതിപ്പിൽ. നന്ദി, നമസ്കാരം."
    return intro + body + outro

async def generate_audio(text, output_file):
    # Free Malayalam Neural Voice
    voice = "ml-IN-SobhanaNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def update_rss_feed(episode_filename, title, description, length_bytes):
    feed_file = "feed.xml"
    ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    tree = ET.parse(feed_file)
    channel = tree.getroot().find('channel')

    # Filled with your GitHub username: intunelife
    base_url = "https://intunelife.github.io/malayalam-news-podcast"
    pub_date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=4))).strftime("%a, %d %b %Y %H:%M:%S +0400")

    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = title
    ET.SubElement(item, 'description').text = description
    ET.SubElement(item, 'pubDate').text = pub_date

    ET.SubElement(item, 'enclosure', {
        'url': f"{base_url}/episodes/{episode_filename}",
        'length': str(length_bytes),
        'type': 'audio/mpeg'
    })
    ET.SubElement(item, 'guid').text = f"ml-news-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"

    tree.write(feed_file, encoding='utf-8', xml_declaration=True)

async def main():
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    output_filename = f"episode_{today_str}.mp3"
    os.makedirs("episodes", exist_ok=True)
    audio_path = os.path.join("episodes", output_filename)

    headlines = get_latest_headlines()
    script = build_script(headlines)

    print("Generating Malayalam Audio...")
    await generate_audio(script, audio_path)

    file_size = os.path.getsize(audio_path)
    episode_title = f"Malayalam News - {datetime.datetime.now().strftime('%B %d, %Y')}"

    update_rss_feed(output_filename, episode_title, "\n".join(headlines), file_size)
    print("Done! feed.xml updated.")

if __name__ == "__main__":
    asyncio.run(main())
