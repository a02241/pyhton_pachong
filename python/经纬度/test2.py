from pypinyin import pinyin, Style

def convert_pinyin_to_chinese(pinyin_str):
    # 将拼音字符串转换为带声调的拼音列表
    pinyin_list = pinyin(pinyin_str, style=Style.NORMAL)

    # 提取拼音列表中的每个拼音字符
    chinese_str = ''.join([p[0] for p in pinyin_list])

    return chinese_str

# 使用示例
pinyin_input = 'wo3 men2 shi4 zhong1 guo2 ren2'
chinese_output = convert_pinyin_to_chinese(pinyin_input)
print(chinese_output)