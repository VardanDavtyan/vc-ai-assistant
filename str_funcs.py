import json

def lowercase_keys(d):
    return {k.lower(): v for k, v in d.items()}

def convert_output_to_dict(data_from_website: str):
    # Remove comments (if any)
    data_from_website = remove_comments(data_from_website)

    start_index = data_from_website.find('{')
    end_index = data_from_website.rfind('}') + 1
    json_data = data_from_website[start_index:end_index]
    return lowercase_keys(json.loads(json_data))


def remove_comments(json_str):
    in_string = False
    in_comment = False
    result = ''
    for i, char in enumerate(json_str):
        if char == '"':
            if i == 0 or json_str[i - 1] != '\\':
                in_string = not in_string
        elif not in_string:
            if char == '/' and not in_comment:
                if i < len(json_str) - 1 and json_str[i + 1] == '/':
                    in_comment = True
                    continue
            elif char == '\n' and in_comment:
                in_comment = False
                continue
        if not in_comment:
            result += char
    return result

def add_br_to_text(text):
  return text.replace("\n", "<br>")

def replace_tabs_with_spaces(text):
    return text.replace("  ", "&emsp;")