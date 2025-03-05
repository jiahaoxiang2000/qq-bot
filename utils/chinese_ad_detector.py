import re
import jieba
from typing import List, Dict, Any, Set, Tuple
from collections import Counter

# Common Chinese advertisement keywords
COMMON_AD_WORDS: Set[str] = {
    # Shopping/Promotions
    "促销",
    "打折",
    "优惠",
    "特价",
    "折扣",
    "团购",
    "秒杀",
    "限时",
    "抢购",
    "特惠",
    "包邮",
    "免费送",
    "礼品",
    "限量",
    "降价",
    "甩卖",
    "一折",
    "二折",
    "半价",
    # Contact methods
    "微信",
    "QQ",
    "加V",
    "私聊",
    "私发",
    "电话",
    "联系",
    "咨询",
    "热线",
    "客服",
    "扫码",
    "关注",
    "添加",
    "群号",
    "入群",
    "加我",
    # Education related
    "考研",
    "考证",
    "培训",
    "辅导",
    "补习",
    "指导",
    "提分",
    "保过",
    "复试",
    "调剂",
    "考试",
    "备考",
    "押题",
    "真题",
    "模拟题",
    "特训",
    "保录",
    "神器",
    "包过",
    # Money/Investment
    "赚钱",
    "投资",
    "理财",
    "收益",
    "回报",
    "股票",
    "基金",
    "保险",
    "贷款",
    "融资",
    "借钱",
    "零息",
    "放贷",
    "担保",
    "信用",
    "资金",
    "合伙",
    "项目",
    # Urgency words
    "抓紧",
    "速来",
    "仅剩",
    "最后",
    "错过",
    "机不可失",
    "立即",
    "马上",
    "赶快",
    "趁早",
    "今日",
    "剩余",
    "名额有限",
    "先到先得",
    # Gaming/Gambling
    "棋牌",
    "博彩",
    "赌博",
    "游戏",
    "充值",
    "代练",
    "刷单",
    "陪玩",
    "代打",
    "金币",
    # Health/Beauty
    "减肥",
    "丰胸",
    "美容",
    "祛斑",
    "增高",
    "壮阳",
    "养生",
    "保健",
    "延时",
    # Job related
    "招聘",
    "求职",
    "简历",
    "应聘",
    "兼职",
    "全职",
    "高薪",
    "待遇",
    "薪资",
    "日结",
    "日薪",
    "周薪",
    "月薪",
    "年薪",
    "提成",
    "佣金",
    "返利",
}

# Common Chinese advertisement patterns
AD_PATTERNS = [
    r"加[V微]信?[:：]?\s*([a-zA-Z0-9_-]{4,20})",
    r"微信[号码]?[:：]?\s*([a-zA-Z0-9_-]{4,20})",
    r"([Qq]{2}|扣扣)[:：]?\s*([0-9]{5,11})",
    r"电话[:：]?\s*(1[3-9]\d{9})",
    r"([加关]注|扫码).{0,5}领.{0,5}(红包|优惠)",
    r"[加关]我.{0,8}发你",
    r"[0-9一二三四五六七八九十百]+[%％].*?折扣",
    r"还差\d{1,2}人.{0,10}(拼团|团购|满减)",
    r"[找要]人.{0,5}一起.{0,5}(考研|调剂|保研)",
    r"本人.{0,20}(专业|精通).{0,20}(辅导|指导)",
    r"(免费|赠送|折扣).{0,15}(咨询|了解|获取)",
]


class ChineseAdDetector:
    """Enhanced Chinese advertisement content detector using only jieba"""

    def __init__(self, custom_keywords: Set[str] = None, threshold: float = 0.15):
        """
        Initialize the detector with optional custom keywords and threshold

        Parameters:
        -----------
        custom_keywords : Set[str], optional
            Additional custom keywords to detect advertisements
        threshold : float, default=0.15
            Threshold for determining if a message is an advertisement
        """
        self.ad_words = COMMON_AD_WORDS.copy()
        if custom_keywords:
            self.ad_words.update(custom_keywords)

        self.threshold = threshold

        # Initialize jieba custom dictionary
        for word in self.ad_words:
            if len(word) >= 2:  # Only add words with length >= 2
                jieba.add_word(
                    word, freq=10, tag="n"
                )  # Add as noun with high frequency

    def is_ad(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Check if text contains advertisement using jieba word segmentation

        Parameters:
        -----------
        text : str
            Text content to be checked

        Returns:
        --------
        Tuple[bool, float, List[str]]
            - Boolean indicating if text is an ad
            - Confidence score (0 to 1)
            - List of matched keywords
        """
        if not text:
            return False, 0.0, []

        # Pattern matching for common ad structures
        for pattern in AD_PATTERNS:
            if re.search(pattern, text):
                return True, 1.0, [f"Pattern match: {pattern}"]

        # Extract words using jieba
        words = list(jieba.cut(text))

        # Check for exact matches
        matched_keywords = [word for word in words if word in self.ad_words]

        # Basic density calculation
        word_count = len(words)
        if word_count > 0:
            ad_density = len(matched_keywords) / word_count
        else:
            ad_density = 0.0

        # Additional detection: check for high concentration of ad words
        if matched_keywords:
            # Count the occurrences of ad words
            ad_word_count = Counter(matched_keywords)
            # If any ad word appears multiple times, increase the score
            repeats = sum(count - 1 for count in ad_word_count.values() if count > 1)
            ad_density = min(1.0, ad_density + (repeats * 0.1))

        # Check for adjacent ad words, which often indicate ad content
        for i in range(len(words) - 1):
            if words[i] in self.ad_words and words[i + 1] in self.ad_words:
                ad_density = min(1.0, ad_density + 0.2)
                break

        return ad_density >= self.threshold, ad_density, matched_keywords

    def analyze_message_segments(
        self, segments: List[Dict[str, Any]]
    ) -> Tuple[bool, float, List[str]]:
        """
        Analyze message segments for advertisement content using jieba

        Parameters:
        -----------
        segments : List[Dict[str, Any]]
            Message segments to analyze

        Returns:
        --------
        Tuple[bool, float, List[str]]
            - Boolean indicating if message contains ads
            - Highest confidence score (0 to 1)
            - List of matched keywords
        """
        is_ad = False
        max_score = 0.0
        all_keywords = []
        combined_text = ""

        # First pass: analyze individual segments
        for segment in segments:
            segment_type = segment.get("type")

            if segment_type == "text":
                content = segment.get("data", {}).get("text", "")
                combined_text += content + " "
                ad_result, score, keywords = self.is_ad(content)

                if ad_result:
                    is_ad = True
                    max_score = max(max_score, score)
                    all_keywords.extend(keywords)

        # Second pass: analyze all text segments combined
        # This helps catch ads that might be split across multiple segments
        if not is_ad and combined_text:
            ad_result, score, keywords = self.is_ad(combined_text)
            if ad_result:
                is_ad = True
                max_score = max(max_score, score)
                all_keywords.extend([k for k in keywords if k not in all_keywords])

        return is_ad, max_score, all_keywords


# Helper function to integrate with existing spam_filter
def is_chinese_ad(message_segments: List[Dict[str, Any]]) -> bool:
    """
    Helper function to check if message segments contain Chinese advertisements

    Parameters:
    -----------
    message_segments : List[Dict[str, Any]]
        Message segments to analyze

    Returns:
    --------
    bool
        True if message contains ads, False otherwise
    """
    detector = ChineseAdDetector()
    is_ad, score, _ = detector.analyze_message_segments(message_segments)
    return is_ad
