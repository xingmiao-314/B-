#!/usr/bin/env python3
"""
游戏角色卡牌AI提示词生成器
生成SDXL格式的英文词组提示词
"""

import random
from typing import List, Dict

# 基础人设特征（固定）
BASE_TRAITS = {
    "hair_color": "pink hair",
    "eye_color": "purple eyes"
}

# R卡：站立平视角度的动作和姿势
R_CARD_POSES = [
    "standing, front view, eye level",
    "standing pose, straight posture, front facing",
    "standing, full body, front view",
    "standing position, facing forward, neutral pose",
    "standing, upright stance, front perspective"
]

# SR卡：透视较大角度、动作多变的姿势
SR_CARD_POSES = [
    "dynamic pose, dramatic perspective, low angle view",
    "action pose, dynamic angle, three-quarter view",
    "dynamic stance, perspective shot, tilted camera angle",
    "action pose, dramatic perspective, upward angle",
    "dynamic movement, perspective view, cinematic angle",
    "action stance, low angle perspective, dynamic composition",
    "dynamic pose, dramatic angle, side view perspective",
    "action pose, perspective shot, dynamic framing",
    "dynamic stance, three-quarter perspective, action view",
    "action pose, dramatic perspective, dynamic angle",
    "dynamic movement, perspective view, action composition",
    "action stance, low angle, dynamic perspective",
    "dynamic pose, dramatic angle, cinematic perspective",
    "action pose, perspective shot, dynamic framing",
    "dynamic stance, three-quarter view, action perspective"
]

# SSR卡：在SR基础上增添性感元素
SSR_CARD_POSES = [
    "seductive pose, dramatic perspective, low angle view, alluring stance",
    "sensual action pose, dynamic angle, three-quarter view, captivating",
    "alluring dynamic stance, perspective shot, seductive pose, elegant",
    "sensual action pose, dramatic perspective, seductive angle, charming",
    "alluring dynamic movement, perspective view, seductive composition, elegant"
]

# 服装变化（具体详细的服装描述，确保20张卡牌不重复）
CLOTHING_STYLES = [
    "white lace summer dress with pink ribbon",
    "black leather jacket over red t-shirt and jeans",
    "blue sailor school uniform with white collar",
    "purple velvet evening gown with silver embroidery",
    "green military-style coat with golden buttons",
    "pink frilly maid outfit with white apron",
    "dark blue wizard robes with star patterns",
    "white wedding dress with long train",
    "red and gold traditional kimono with cherry blossoms",
    "silver futuristic armor with glowing blue accents",
    "yellow sundress with sunflower patterns",
    "black gothic lolita dress with white lace trim",
    "orange sports jersey with number 7",
    "navy blue business suit with white shirt",
    "pastel pink cardigan over white blouse",
    "emerald green ball gown with crystal decorations",
    "brown leather adventurer outfit with belt pouches",
    "white nurse uniform with red cross",
    "rainbow striped sweater with denim shorts",
    "golden warrior armor with red cape"
]

# 背景变化（具体详细的背景描述，确保20张卡牌不重复）
BACKGROUND_STYLES = [
    "sakura cherry blossom park in spring afternoon",
    "neon-lit cyberpunk city street at night",
    "ancient gothic cathedral interior with stained glass windows",
    "tropical beach with palm trees and turquoise ocean",
    "snow-covered mountain peak at sunrise",
    "cozy coffee shop interior with warm lighting",
    "magical forest with glowing mushrooms and fireflies",
    "modern art gallery with white walls and spotlights",
    "medieval castle courtyard with stone walls",
    "space station observation deck with earth view",
    "japanese garden with koi pond and red bridge",
    "abandoned factory with rusted machinery",
    "starry night sky over desert dunes",
    "victorian library with tall bookshelves",
    "underwater coral reef with colorful fish",
    "autumn maple forest with red and orange leaves",
    "futuristic laboratory with holographic displays",
    "traditional japanese tea room with tatami mats",
    "concert hall stage with grand piano",
    "sunset over city skyline from rooftop"
]

# 表情和情绪
EXPRESSIONS = [
    "smiling",
    "serious expression",
    "confident look",
    "gentle smile",
    "determined face",
    "calm expression",
    "happy expression",
    "mysterious look",
    "bright expression",
    "cool expression"
]

# SDXL格式的通用质量标签
QUALITY_TAGS = [
    "high quality",
    "detailed",
    "beautiful",
    "professional",
    "masterpiece",
    "best quality",
    "ultra detailed",
    "8k resolution"
]


def generate_card_prompt(card_type: str, pose: str, clothing: str, background: str, 
                        expression: str, traits: Dict[str, str]) -> str:
    """
    生成单张卡牌的提示词
    
    Args:
        card_type: 卡牌类型 (R/SR/SSR)
        pose: 姿势描述
        clothing: 服装描述
        background: 背景描述
        expression: 表情描述
        traits: 角色特征（头发、眼睛颜色等）
    
    Returns:
        SDXL格式的英文词组提示词
    """
    # 基础特征（固定）
    base_features = [
        traits["hair_color"],
        traits["eye_color"],
        "character card",
        "game character",
        "anime style",
        "illustration"
    ]
    
    # 根据卡牌类型添加特定元素（避免与pose重复）
    if card_type == "R":
        card_specific = [
            "simple composition"
        ]
    elif card_type == "SR":
        card_specific = [
            "action scene"
        ]
    else:  # SSR
        card_specific = [
            "alluring pose",
            "sensual",
            "elegant",
            "captivating"
        ]
    
    # 组合所有元素
    prompt_parts = (
        QUALITY_TAGS +
        base_features +
        [pose] +
        card_specific +
        [clothing] +
        [background] +
        [expression]
    )
    
    # 转换为词组格式（逗号分隔）
    prompt = ", ".join(prompt_parts)
    
    return prompt


def generate_character_cards(character_name: str, traits: Dict[str, str], 
                             r_count: int = 5, sr_count: int = 15, ssr_count: int = 5) -> Dict[str, List[str]]:
    """
    为单个角色生成所有卡牌的提示词
    
    Args:
        character_name: 角色名称
        traits: 角色特征
        r_count: R卡数量
        sr_count: SR卡数量
        ssr_count: SSR卡数量
    
    Returns:
        包含所有卡牌提示词的字典
    """
    cards = {
        "R": [],
        "SR": [],
        "SSR": []
    }
    
    # 确保所有卡牌使用不同的服装和背景组合
    total_cards = r_count + sr_count + ssr_count
    used_clothing = set()
    used_background = set()
    
    # 打乱列表以确保随机性
    clothing_list = CLOTHING_STYLES.copy()
    background_list = BACKGROUND_STYLES.copy()
    random.shuffle(clothing_list)
    random.shuffle(background_list)
    
    clothing_idx = 0
    background_idx = 0
    
    # 生成R卡
    for i in range(r_count):
        # 确保服装和背景不重复
        while clothing_list[clothing_idx % len(clothing_list)] in used_clothing:
            clothing_idx += 1
        while background_list[background_idx % len(background_list)] in used_background:
            background_idx += 1
        
        clothing = clothing_list[clothing_idx % len(clothing_list)]
        background = background_list[background_idx % len(background_list)]
        expression = random.choice(EXPRESSIONS)
        pose = R_CARD_POSES[i % len(R_CARD_POSES)]
        
        used_clothing.add(clothing)
        used_background.add(background)
        clothing_idx += 1
        background_idx += 1
        
        prompt = generate_card_prompt("R", pose, clothing, background, expression, traits)
        cards["R"].append(prompt)
    
    # 生成SR卡
    for i in range(sr_count):
        # 确保服装和背景不重复
        while clothing_list[clothing_idx % len(clothing_list)] in used_clothing:
            clothing_idx += 1
        while background_list[background_idx % len(background_list)] in used_background:
            background_idx += 1
        
        clothing = clothing_list[clothing_idx % len(clothing_list)]
        background = background_list[background_idx % len(background_list)]
        expression = random.choice(EXPRESSIONS)
        pose = SR_CARD_POSES[i % len(SR_CARD_POSES)]
        
        used_clothing.add(clothing)
        used_background.add(background)
        clothing_idx += 1
        background_idx += 1
        
        prompt = generate_card_prompt("SR", pose, clothing, background, expression, traits)
        cards["SR"].append(prompt)
    
    # 生成SSR卡
    for i in range(ssr_count):
        # 确保服装和背景不重复
        while clothing_list[clothing_idx % len(clothing_list)] in used_clothing:
            clothing_idx += 1
        while background_list[background_idx % len(background_list)] in used_background:
            background_idx += 1
        
        clothing = clothing_list[clothing_idx % len(clothing_list)]
        background = background_list[background_idx % len(background_list)]
        expression = random.choice(EXPRESSIONS)
        pose = SSR_CARD_POSES[i % len(SSR_CARD_POSES)]
        
        used_clothing.add(clothing)
        used_background.add(background)
        clothing_idx += 1
        background_idx += 1
        
        prompt = generate_card_prompt("SSR", pose, clothing, background, expression, traits)
        cards["SSR"].append(prompt)
    
    return cards


def main():
    """主函数：生成第一个角色的卡牌提示词"""
    # 设置随机种子以确保可重现性（可选）
    random.seed(42)
    
    # 第一个角色：粉色头发、紫色眼睛
    character_traits = {
        "hair_color": "pink hair",
        "eye_color": "purple eyes"
    }
    
    print("=" * 80)
    print("游戏角色卡牌AI提示词生成器")
    print("=" * 80)
    print(f"\n角色特征：{character_traits['hair_color']}, {character_traits['eye_color']}")
    print("\n生成卡牌提示词...\n")
    
    # 生成卡牌
    cards = generate_character_cards("Character 1", character_traits, r_count=5, sr_count=15, ssr_count=5)
    
    # 输出结果
    print("=" * 80)
    print("R卡提示词 (5张)")
    print("=" * 80)
    for i, prompt in enumerate(cards["R"], 1):
        print(f"\nR卡 #{i}:")
        print(prompt)
    
    print("\n" + "=" * 80)
    print("SR卡提示词 (15张)")
    print("=" * 80)
    for i, prompt in enumerate(cards["SR"], 1):
        print(f"\nSR卡 #{i}:")
        print(prompt)
    
    print("\n" + "=" * 80)
    print("SSR卡提示词 (5张)")
    print("=" * 80)
    for i, prompt in enumerate(cards["SSR"], 1):
        print(f"\nSSR卡 #{i}:")
        print(prompt)
    
    print("\n" + "=" * 80)
    print("生成完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()

