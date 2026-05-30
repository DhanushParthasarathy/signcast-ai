from html import escape


class ThumbnailService:
    def generate_svg_thumbnail(self, gloss: str) -> bytes:
        label = escape(gloss)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#17202a"/>
  <rect x="56" y="56" width="1168" height="608" rx="24" fill="#f7f8f5"/>
  <text x="640" y="330" text-anchor="middle" font-family="Arial, sans-serif" font-size="84" font-weight="700" fill="#17202a">{label}</text>
  <text x="640" y="410" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" fill="#566b7b">SignCast AI sign clip</text>
</svg>"""
        return svg.encode("utf-8")
