def build_lps(pattern):
    lps = [0] * len(pattern)

    length = 0
    i = 1

    while i < len(pattern):
        if pattern[i].lower() == pattern[length].lower():
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def kmp_search(text, pattern):
    if not pattern:
        return []

    lps = build_lps(pattern)

    matches = []
    i = 0
    j = 0

    while i < len(text):
        if text[i].lower() == pattern[j].lower():
            i += 1
            j += 1

        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and text[i].lower() != pattern[j].lower():
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return matches