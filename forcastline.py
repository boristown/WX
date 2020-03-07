
def get_version(input_text):
    if 'V1' in input_text:
        input_text.replace("V1", "")
        return input_text, "V1"
    if 'V2' in input_text:
        input_text.replace("V2", "")
        return input_text, "V2"
    return input_text, "V1"