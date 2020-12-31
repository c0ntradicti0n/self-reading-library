import regex

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def insert(i, string_s, insert_s):
    return string_s[:i] + insert_s + string_s[i:]

def insert_at_index(string, index, to_insert):
    return string[:index] + to_insert + string[index:]

def remove_ugly_chars(string):
    string = string.replace("'", "").replace(" ","_").replace(".","_")
    return regex.sub(r"[\n\t\:\$ \\\!\@\#\$\%\^\&\*\(\)\-\+\=\'\"\;\<\>\?\/\~\`\.\,\;]", "_", string, regex.MULTILINE)

