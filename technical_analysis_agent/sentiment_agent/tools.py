import json
import os
import time
import yfinance as yf

CACHE_EXPIRATION_SECONDS = 24 * 60 * 60  # Cache news for 24 hours

def get_ticker_news(ticker: str) -> str:
    """
    Fetches the latest news articles for the stock ticker using yfinance,
    extracts the headlines, summaries, and sources, and returns them formatted.
    Checks local cache first.
    """
    # Sanitize the input ticker to prevent path traversal
    safe_ticker = os.path.basename(ticker)
    safe_ticker = "".join(c for c in safe_ticker if c.isalnum() or c in ".-")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_lake_dir = os.path.abspath(os.path.join(current_dir, "..", "local_data_lake"))
    os.makedirs(data_lake_dir, exist_ok=True)
    file_path = os.path.join(data_lake_dir, f"{safe_ticker}_news.json")
    
    # 1. CHECK CACHE
    if os.path.exists(file_path) and (time.time() - os.path.getmtime(file_path)) < CACHE_EXPIRATION_SECONDS:
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception:
            pass  # Fall back to fetching fresh data if cache read fails
            
    # 2. FETCH NEW DATA
    try:
        stock = yf.Ticker(ticker)
        news_list = stock.news
        
        if not news_list:
            return json.dumps({
                "ticker": ticker, 
                "news": [], 
                "message": f"No news articles found for {ticker}."
            })
            
        formatted_news = []
        for item in news_list:
            content = item.get("content", {})
            title = content.get("title", "")
            summary = content.get("summary", "")
            pub_date = content.get("pubDate", "") or content.get("displayTime", "")
            provider = content.get("provider", {}).get("displayName", "")
            url = content.get("canonicalUrl", {}).get("url", "") or content.get("clickThroughUrl", {}).get("url", "")
            
            if title or summary:
                formatted_news.append({
                    "title": title,
                    "summary": summary,
                    "published_at": pub_date,
                    "source": provider,
                    "url": url
                })
        
        final_payload = {
            "ticker": ticker,
            "news": formatted_news
        }
        
        json_output = json.dumps(final_payload, indent=4)
        
        # 3. SAVE & RETURN
        with open(file_path, "w") as f:
            f.write(json_output)
            
        return json_output
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch news for {ticker}: {str(e)}"})
