import re
import json
from typing import List, Dict, Union, Any, Optional


def process_json_message(json_data: Dict[str, Any]) -> bool:
    """
    Process JSON message segment to check if it contains advertising

    Parameters
    ----------
    json_data : Dict[str, Any]
        JSON data extracted from a message segment

    Returns
    -------
    bool
        True if the message contains advertising, False otherwise
    """
    try:
        if not isinstance(json_data, dict) or "data" not in json_data:
            return False

        # Extract the inner data field which contains the JSON string
        inner_data = json_data.get("data", {}).get("data")
        if not inner_data:
            return False

        # Parse the JSON string into a Python object
        content = json.loads(inner_data)

        # Check for common advertising indicators
        if "prompt" in content and (
            "分享" in content["prompt"] or "链接" in content["prompt"]
        ):
            # Check meta data for URLs or jumpUrl
            if "meta" in content:
                meta = content.get("meta", {})

                # Check for news with jumpUrl
                if "news" in meta and "jumpUrl" in meta["news"]:
                    return True

                # Check for tags related to advertising
                if "news" in meta and "tag" in meta["news"]:
                    if meta["news"]["tag"] in ["微信", "广告", "推广"]:
                        return True

            # Check for specific keywords in the title or description
            if "meta" in content and "news" in content["meta"]:
                news = content["meta"]["news"]
                title = news.get("title", "")
                desc = news.get("desc", "")

                ad_keywords = [
                    "团购",
                    "优惠",
                    "促销",
                    "折扣",
                    "抢购",
                    "限时",
                    "免费领取",
                    "点击链接",
                    "私聊",
                    "微信",
                    "加v",
                    "咨询",
                    "指导",
                    "调剂",
                    "考研",
                    "复试",
                    "团差",
                ]

                for keyword in ad_keywords:
                    if keyword in title or keyword in desc:
                        return True

            # Look for URLs in any part of the content
            content_str = str(content)
            url_patterns = ["https?://\\S+", "www\\.\\S+", "\\.com/\\S+", "\\.cn/\\S+"]

            for pattern in url_patterns:
                if re.search(pattern, content_str):
                    return True

    except (json.JSONDecodeError, TypeError, ValueError) as e:
        # If there's an error parsing, assume it's not an ad
        return False

    return False


def is_advertising_in_segments(message_segments: List[Dict[str, Any]]) -> bool:
    """
    Check if any segment in the message contains advertising

    Parameters
    ----------
    message_segments : List[Dict[str, Any]]
        List of message segments from the message field

    Returns
    -------
    bool
        True if any segment contains advertising, False otherwise
    """
    for segment in message_segments:
        segment_type = segment.get("type")

        # Check JSON type segments which are commonly used for advertisements
        if segment_type == "json":
            if process_json_message(segment):
                return True

    return False


# Import the Chinese Ad Detector if available
try:
    from .chinese_ad_detector import is_chinese_ad

    CHINESE_AD_DETECTOR_AVAILABLE = True
except ImportError:
    CHINESE_AD_DETECTOR_AVAILABLE = False


# Enhanced version of is_advertising_in_segments that uses Chinese ad detector if available
def is_advertising_in_segments_enhanced(message_segments: List[Dict[str, Any]]) -> bool:
    """
    Enhanced version that also uses the Chinese ad detector if available

    Parameters
    ----------
    message_segments : List[Dict[str, Any]]
        List of message segments from the message field

    Returns
    -------
    bool
        True if any segment contains advertising, False otherwise
    """
    # First check with the basic method
    if is_advertising_in_segments(message_segments):
        return True

    # Then use the enhanced Chinese detector if available
    if CHINESE_AD_DETECTOR_AVAILABLE:
        return is_chinese_ad(message_segments)

    return False
