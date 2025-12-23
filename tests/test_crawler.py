from src.data.ingestion.web_crawler import fetch_url_text

urls = [
    "https://en.wikipedia.org/wiki/Fourpence_(British_coin)",
]

for u in urls:
    print("=== URL:", u)
    res = fetch_url_text(u)
    # Print basic diagnostics
    print("Title:", res.get("title"))
    print("Printing first 2000 characters :",res.get("text","")[:1000])
    print("Text length:", len(res.get("text","")))
    if res.get("error"):
        print("Error:", res["error"])
    print("-" * 60)
